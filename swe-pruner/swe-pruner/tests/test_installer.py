import hashlib
import importlib.util
import io
import json
import os
import subprocess
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

    def test_complete_partial_download_is_promoted_without_downloading_again(self):
        self.cache.mkdir()
        (self.cache / (self.model["sha256"] + ".part")).write_bytes(self.body)
        with patch.object(installer.urllib.request, "urlopen") as request:
            self.assertEqual(installer.download_model(self.model, self.cache).read_bytes(), self.body)
            request.assert_not_called()

    def install_fixture(self):
        bundle = self.manifest()
        config = bundle / installer.BACKEND / "model/config.json"
        config.parent.mkdir(parents=True)
        config.write_text("{}", encoding="utf-8")
        manifest_file = bundle / "backend-manifest.json"
        manifest = json.loads(manifest_file.read_text())
        manifest["files"].append({"path": config.relative_to(bundle).as_posix(), "size": 2, "sha256": installer.checksum(config)})
        manifest_file.write_text(json.dumps(manifest), encoding="utf-8")
        storage = self.root / "storage"
        local = self.root / "model.safetensors"
        local.write_bytes(self.body)
        return bundle, storage, local

    @staticmethod
    def fake_execute(arguments, **kwargs):
        if "venv" in arguments:
            venv = Path(arguments[-1])
            python = venv / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
            python.parent.mkdir(parents=True, exist_ok=True)
            python.write_bytes(b"private interpreter fixture")

    @staticmethod
    def pip_calls(mock):
        return [call.args[0] for call in mock.call_args_list if call.args[0][1:3] == ["-m", "pip"]]

    def test_model_failure_retry_reuses_all_verified_dependency_steps(self):
        bundle, storage, local = self.install_fixture()
        with patch.object(installer, "execute", side_effect=self.fake_execute) as command, \
             patch.object(installer.urllib.request, "urlopen", side_effect=OSError("offline")):
            with self.assertRaisesRegex(OSError, "offline"):
                installer.install(bundle, storage, "0.6.0")
            self.assertEqual(len(self.pip_calls(command)), 3)
            command.reset_mock()
            result = installer.install(bundle, storage, "0.6.0", local)
            self.assertEqual(self.pip_calls(command), [])
            self.assertTrue((result / "managed-install.json").exists())
            self.assertEqual(json.loads((result / "setup-state.json").read_text())["completed"], ["dependencies", "tools", "torch"])

    def test_failed_dependency_step_is_not_checkpointed_and_can_resume(self):
        bundle, storage, local = self.install_fixture()
        failed = False
        def execute(arguments, **kwargs):
            nonlocal failed
            self.fake_execute(arguments, **kwargs)
            if f"torch=={installer.TORCH_VERSION}" in arguments and not failed:
                failed = True
                raise subprocess.CalledProcessError(1, arguments)
        with patch.object(installer, "execute", side_effect=execute) as command:
            with self.assertRaises(subprocess.CalledProcessError):
                installer.install(bundle, storage, "0.6.0", local)
            checkpoint = next((storage / "backend/managed").glob("*/setup-state.json"))
            self.assertEqual(json.loads(checkpoint.read_text())["completed"], ["tools"])
            command.reset_mock()
            installer.install(bundle, storage, "0.6.0", local)
            self.assertEqual(len(self.pip_calls(command)), 2)
            self.assertTrue(any(f"torch=={installer.TORCH_VERSION}" in args for args in self.pip_calls(command)))

    def test_invalid_checkpoint_does_not_skip_dependency_installation(self):
        bundle, storage, local = self.install_fixture()
        with patch.object(installer, "execute", side_effect=self.fake_execute) as command:
            result = installer.install(bundle, storage, "0.6.0", local)
            (result / "setup-state.json").write_text("broken checkpoint", encoding="utf-8")
            command.reset_mock()
            installer.install(bundle, storage, "0.6.0", local)
            self.assertEqual(len(self.pip_calls(command)), 3)

    def test_failed_reuse_check_repairs_the_affected_dependency_step(self):
        bundle, storage, local = self.install_fixture()
        with patch.object(installer, "execute", side_effect=self.fake_execute):
            installer.install(bundle, storage, "0.6.0", local)
        failed = False
        def execute(arguments, **kwargs):
            nonlocal failed
            if "-c" in arguments and arguments[-1].startswith("import torch;") and not failed:
                failed = True
                raise subprocess.CalledProcessError(1, arguments)
            self.fake_execute(arguments, **kwargs)
        with patch.object(installer, "execute", side_effect=execute) as command:
            installer.install(bundle, storage, "0.6.0", local)
            self.assertEqual(len(self.pip_calls(command)), 1)
            self.assertIn("--force-reinstall", self.pip_calls(command)[0])

    def test_broken_private_environment_is_recreated_and_rechecked(self):
        bundle, storage, local = self.install_fixture()
        with patch.object(installer, "execute", side_effect=self.fake_execute):
            installer.install(bundle, storage, "0.6.0", local)
        def execute(arguments, **kwargs):
            if "-c" in arguments and "import sys, struct, pip" in arguments[-1]:
                raise OSError("private Python is broken")
            self.fake_execute(arguments, **kwargs)
        with patch.object(installer, "execute", side_effect=execute) as command:
            installer.install(bundle, storage, "0.6.0", local)
            self.assertTrue(any("--clear" in call.args[0] for call in command.call_args_list))
            self.assertEqual(len(self.pip_calls(command)), 3)

    def test_dependency_repair_keeps_the_cpu_torch_build(self):
        bundle, storage, local = self.install_fixture()
        with patch.object(installer, "execute", side_effect=self.fake_execute):
            installer.install(bundle, storage, "0.6.0", local)
        failed = False
        def execute(arguments, **kwargs):
            nonlocal failed
            if "-c" in arguments and "import fastapi, uvicorn, transformers" in arguments[-1] and not failed:
                failed = True
                raise subprocess.CalledProcessError(1, arguments)
            self.fake_execute(arguments, **kwargs)
        with patch.object(installer.sys, "platform", "win32"), patch.object(installer, "execute", side_effect=execute) as command:
            installer.install(bundle, storage, "0.6.0", local)
            calls = self.pip_calls(command)
            self.assertEqual(len(calls), 1)
            self.assertIn(f"torch=={installer.TORCH_VERSION}+cpu", calls[0])
            self.assertIn("https://download.pytorch.org/whl/cpu", calls[0])
            self.assertIn("--force-reinstall", calls[0])

    def test_structured_failure_identifies_the_step_and_recovery_hint(self):
        bundle = self.manifest()
        output = io.StringIO()
        with patch.object(installer.sys, "argv", ["install_backend.py", "--bundle", str(bundle), "--storage", str(self.root / "storage"), "--version", "0.6.0"]), \
             patch.object(installer, "execute", side_effect=OSError("not enough disk space")), \
             patch.object(installer.sys, "stderr", output):
            self.assertEqual(installer.main(), 1)
        record = next(line for line in output.getvalue().splitlines() if line.startswith("TOKENWISE_SETUP_ERROR "))
        failure = json.loads(record.split(" ", 1)[1])
        self.assertEqual(failure["stage"], "environment")
        self.assertEqual(failure["step"], 3)
        self.assertIn("permissions", failure["hint"])

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
