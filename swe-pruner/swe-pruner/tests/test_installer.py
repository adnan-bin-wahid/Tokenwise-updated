import hashlib
import importlib.util
import io
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location("tokenwise_installer", ROOT / "scripts/install_backend.py")
installer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)


class Response(io.BytesIO):
    def __init__(self, body, status=200, content_range=None):
        super().__init__(body)
        self.status = status
        self.headers = {"Content-Range": content_range}

    def geturl(self):
        return "https://download.example.test/verified-model"


class InstallerTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.root = Path(self.directory.name).resolve()
        self.addCleanup(self.directory.cleanup)
        self.body = b"verified model fixture"
        self.model = {
            "repository": "ayanami-kitasan/code-pruner", "revision": "a" * 40,
            "sha256": hashlib.sha256(self.body).hexdigest(), "size": len(self.body),
            "url": "https://huggingface.co/ayanami-kitasan/code-pruner/resolve/" + "a" * 40 + "/model.safetensors",
        }
        self.cache = self.root / "cache"

    def manifest(self):
        bundle = self.root / "bundle"
        source = bundle / "scripts/example.py"
        source.parent.mkdir(parents=True)
        source.write_bytes(b"print('safe')\n")
        manifest = {"schema_version": 1, "model": self.model, "files": [{
            "path": "scripts/example.py", "size": source.stat().st_size, "sha256": installer.checksum(source),
        }]}
        (bundle / "backend-manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
        return bundle

    def test_manifest_checks_bundled_file_integrity(self):
        bundle = self.manifest()
        manifest, fingerprint = installer.load_manifest(bundle)
        self.assertEqual(len(fingerprint), 64)
        self.assertEqual(manifest["model"]["sha256"], self.model["sha256"])
        (bundle / "scripts/example.py").write_text("tampered", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "failed verification"):
            installer.load_manifest(bundle)

    def test_path_traversal_and_absolute_targets_are_rejected(self):
        for name in ("../outside", "/absolute", "C:/outside", "scripts/../../outside", "scripts\\outside"):
            with self.subTest(path=name), self.assertRaises(ValueError):
                installer.safe_path(self.root, name)

    def test_model_metadata_cannot_redirect_to_another_download(self):
        bundle = self.manifest()
        path = bundle / "backend-manifest.json"
        data = json.loads(path.read_text())
        data["model"]["url"] = "https://other.example.test/model"
        path.write_text(json.dumps(data))
        with self.assertRaisesRegex(ValueError, "Invalid pinned"):
            installer.load_manifest(bundle)

    def test_complete_download_is_verified_before_cache_promotion(self):
        with patch.object(installer.urllib.request, "urlopen", return_value=Response(self.body)):
            result = installer.download_model(self.model, self.cache)
        self.assertEqual(result.read_bytes(), self.body)
        self.assertFalse((self.cache / (self.model["sha256"] + ".part")).exists())

    def test_verified_cache_does_not_make_a_network_request(self):
        self.cache.mkdir()
        cached = self.cache / (self.model["sha256"] + ".safetensors")
        cached.write_bytes(self.body)
        with patch.object(installer.urllib.request, "urlopen") as request:
            self.assertEqual(installer.download_model(self.model, self.cache), cached)
            request.assert_not_called()

    def test_partial_download_resumes_with_valid_byte_range(self):
        self.cache.mkdir()
        (self.cache / (self.model["sha256"] + ".part")).write_bytes(self.body[:8])
        response = Response(self.body[8:], 206, f"bytes 8-{len(self.body)-1}/{len(self.body)}")
        with patch.object(installer.urllib.request, "urlopen", return_value=response) as request:
            result = installer.download_model(self.model, self.cache)
        self.assertEqual(request.call_args.args[0].get_header("Range"), "bytes=8-")
        self.assertEqual(result.read_bytes(), self.body)

    def test_server_without_range_support_restarts_instead_of_appending(self):
        self.cache.mkdir()
        (self.cache / (self.model["sha256"] + ".part")).write_bytes(self.body[:8])
        with patch.object(installer.urllib.request, "urlopen", return_value=Response(self.body, 200)):
            self.assertEqual(installer.download_model(self.model, self.cache).read_bytes(), self.body)

    def test_invalid_resume_response_preserves_partial_for_a_later_retry(self):
        self.cache.mkdir()
        partial = self.cache / (self.model["sha256"] + ".part")
        partial.write_bytes(self.body[:8])
        with patch.object(installer.urllib.request, "urlopen", return_value=Response(self.body[8:], 206, "invalid")):
            with self.assertRaisesRegex(ValueError, "resume"):
                installer.download_model(self.model, self.cache)
        self.assertEqual(partial.read_bytes(), self.body[:8])

    def test_corrupt_download_is_not_promoted_and_is_discarded(self):
        with patch.object(installer.urllib.request, "urlopen", return_value=Response(b"x" * len(self.body))):
            with self.assertRaisesRegex(ValueError, "integrity"):
                installer.download_model(self.model, self.cache)
        self.assertEqual(list(self.cache.iterdir()), [])

    def test_truncated_download_is_kept_for_resume(self):
        with patch.object(installer.urllib.request, "urlopen", return_value=Response(self.body[:8])):
            with self.assertRaisesRegex(ValueError, "resume"):
                installer.download_model(self.model, self.cache)
        self.assertEqual((self.cache / (self.model["sha256"] + ".part")).read_bytes(), self.body[:8])

    def test_local_weights_are_checked_before_copying(self):
        local = self.root / "local.safetensors"
        local.write_bytes(self.body)
        with patch.object(installer.urllib.request, "urlopen") as request:
            self.assertEqual(installer.download_model(self.model, self.cache, local).read_bytes(), self.body)
            request.assert_not_called()

    def test_failed_setup_releases_its_owned_lock(self):
        bundle = self.manifest()
        storage = self.root / "storage"
        with patch.object(installer, "execute", side_effect=RuntimeError("dependency failure")):
            with self.assertRaisesRegex(RuntimeError, "dependency failure"):
                installer.install(bundle, storage, "0.4.0")
        self.assertFalse((storage / "backend/install.lock").exists())

    def test_another_installers_lock_is_not_removed(self):
        bundle = self.manifest()
        storage = self.root / "storage"
        (storage / "backend").mkdir(parents=True)
        lock = storage / "backend/install.lock"
        lock.write_text("other installer")
        with self.assertRaisesRegex(ValueError, "Another backend setup"):
            installer.install(bundle, storage, "0.4.0")
        self.assertEqual(lock.read_text(), "other installer")


if __name__ == "__main__":
    unittest.main()
