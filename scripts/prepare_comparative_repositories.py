"""Prepare pinned upstream workspaces without installing or executing their code."""
from __future__ import annotations

import argparse
import ast
import csv
import hashlib
import io
import json
import re
import stat
from pathlib import Path, PurePosixPath
from urllib.request import Request, urlopen
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'evaluation' / 'comparative-study'
DESTINATION = ROOT / 'demonstration' / 'comparative_study'
ARCHIVES = ROOT / 'tmp' / 'comparative-study' / 'archives'
MAX_ARCHIVE = 30 * 1024 * 1024
MAX_EXPANDED = 100 * 1024 * 1024
MAX_FILE = 20 * 1024 * 1024


def archive_files(content: bytes) -> tuple[list[tuple[Path, bytes]], list[str]]:
    """Validate the complete archive before any destination file is written."""
    files, skipped, seen, prefix, size = [], [], set(), None, 0
    with ZipFile(io.BytesIO(content)) as archive:
        for item in archive.infolist():
            name = item.orig_filename
            parts = PurePosixPath(name).parts
            if not parts or name.startswith('/') or '\\' in name or ':' in name:
                raise ValueError(f'Unsafe archive member: {name}')
            if any(part in {'.', '..'} or part.endswith((' ', '.')) for part in parts):
                raise ValueError(f'Unsafe archive member: {name}')
            if prefix is None:
                prefix = parts[0]
            if parts[0] != prefix:
                raise ValueError('Archive must contain one repository root')
            if len(parts) == 1 or item.is_dir():
                continue
            relative = Path(*parts[1:])
            if any(part.lower() == '.git' for part in parts[1:]):
                raise ValueError('Repository archives must not contain Git internals')
            mode = stat.S_IFMT(item.external_attr >> 16)
            if mode not in {0, stat.S_IFREG}:
                skipped.append(relative.as_posix())
                continue
            key = relative.as_posix().casefold()
            if key in seen:
                raise ValueError(f'Duplicate archive target: {relative}')
            seen.add(key)
            size += item.file_size
            if size > MAX_EXPANDED or item.file_size > MAX_FILE:
                raise ValueError('Expanded archive exceeds the corpus safety limit')
            files.append((relative, archive.read(item)))
    if not files:
        raise ValueError('Archive has no regular files')
    return files, skipped


def checked_target(directory: Path, relative: Path) -> Path:
    target = directory / relative
    if not target.resolve().is_relative_to(directory.resolve()):
        raise ValueError(f'Destination escapes the workspace: {relative}')
    for candidate in [target, *target.parents]:
        if candidate == directory.parent:
            break
        if candidate.is_symlink() or candidate.is_junction():
            raise ValueError(f'Refusing a linked destination: {candidate}')
    return target


def prepare_files(directory: Path, files: list[tuple[Path, bytes]]) -> tuple[int, int]:
    """Retry missing files safely, but never replace a user's changed source."""
    pending = []
    verified = 0
    for relative, content in files:
        target = checked_target(directory, relative)
        if target.exists():
            if not target.is_file() or target.read_bytes() != content:
                raise ValueError(f'Existing file differs; preserved without overwrite: {target}')
            verified += 1
        else:
            pending.append((target, content))
    for target, content in pending:
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open('xb') as stream:
            stream.write(content)
    return len(pending), verified


def load_archive(repository: str, snapshot: dict, download: bool) -> bytes:
    commit = snapshot['commit']
    if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', repository):
        raise ValueError('Invalid GitHub repository identifier')
    if not re.fullmatch(r'[0-9a-f]{40}', commit):
        raise ValueError('Expected a pinned forty-character commit')
    path = ARCHIVES / f'{repository.replace("/", "--")}-{commit}.zip'
    if path.exists():
        if path.stat().st_size > MAX_ARCHIVE:
            raise ValueError(f'Archive exceeds the download limit: {path}')
        content = path.read_bytes()
    else:
        if not download:
            raise FileNotFoundError(f'Missing {path.name}; rerun with --download to retrieve the pinned archive')
        url = f'https://codeload.github.com/{repository}/zip/{commit}'
        request = Request(url, headers={'User-Agent': 'TokenWise-Comparative-Demonstration'})
        with urlopen(request, timeout=120) as response:
            if not response.geturl().startswith('https://codeload.github.com/'):
                raise ValueError('Unexpected archive redirect')
            content = response.read(MAX_ARCHIVE + 1)
        if len(content) > MAX_ARCHIVE:
            raise ValueError('Archive exceeds the download limit')
    if hashlib.sha256(content).hexdigest() != snapshot['archive_sha256']:
        raise ValueError(f'Archive SHA-256 does not match the recorded study: {repository}')
    if not path.exists():
        ARCHIVES.mkdir(parents=True, exist_ok=True)
        with path.open('xb') as stream:
            stream.write(content)
    return content


def symbol_names(tree: ast.AST, prefix=''):
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            name = prefix + node.name
            yield name
            if isinstance(node, ast.ClassDef):
                yield from symbol_names(node, name + '.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--download', action='store_true', help='Download missing pinned archives from public GitHub')
    args = parser.parse_args()
    cases = json.loads((DATA / 'cases.json').read_text(encoding='utf-8'))['cases']
    snapshots = json.loads((DATA / 'snapshots.json').read_text(encoding='utf-8'))
    if len(cases) != 20 or len({case['repository'] for case in cases}) != 20:
        raise ValueError('Expected twenty distinct recorded study repositories')
    DESTINATION.mkdir(parents=True, exist_ok=True)
    records = []
    for number, case in enumerate(cases, start=1):
        repository = case['repository']
        snapshot = snapshots[repository]
        if snapshot['ref'] != case['ref']:
            raise ValueError(f'Case / snapshot reference mismatch: {repository}')
        folder = f'{number:02d}_{repository.split("/")[1]}'
        directory = checked_target(DESTINATION, Path(folder))
        content = load_archive(repository, snapshot, args.download)
        files, skipped = archive_files(content)
        selected = next((text for path, text in files if path.as_posix() == case['file']), None)
        if selected is None or case['symbol'] not in set(symbol_names(ast.parse(selected))):
            raise ValueError(f'The requested study symbol is missing: {repository}')
        if not any(path.name.upper().startswith(('LICENSE', 'LICENCE', 'COPYING')) for path, _ in files):
            raise ValueError(f'Upstream license is missing: {repository}')
        created, verified = prepare_files(directory, files)
        digest = hashlib.sha256()
        for path, data in sorted(files, key=lambda item: item[0].as_posix()):
            digest.update(path.as_posix().encode('utf-8') + b'\0')
            digest.update(hashlib.sha256(data).digest())
        records.append({
            'number': number, 'folder': folder, 'repository': repository,
            'ref': case['ref'], 'commit': snapshot['commit'], 'source_url': snapshot['source_url'],
            'archive_sha256': snapshot['archive_sha256'], 'upstream_files': len(files),
            'python_files_in_archive': sum(path.suffix == '.py' for path, _ in files),
            'source_bytes': sum(len(data) for _, data in files),
            'regular_file_fingerprint': digest.hexdigest(), 'skipped_nonregular_members': skipped,
            'task': case['query'], 'target_file': case['file'], 'target_symbol': case['symbol'],
        })
        print(f'{folder}: {created} created, {verified} verified; target symbol and license checked', flush=True)
    manifest = {'format_version': 1, 'corpus': 'Pinned public source archives for manual paired demonstration',
                'source_cases': '../../evaluation/comparative-study/cases.json',
                'source_snapshots': '../../evaluation/comparative-study/snapshots.json',
                'repository_code_executed': False, 'live_agent_runs_performed': False,
                'repositories': records}
    (DESTINATION / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    prompt_lines = ['# Repository Tasks', '', 'Open only the numbered project folder, not this parent folder.',
                    'Use the identical prompt in independent WITHOUT and WITH chats.',
                    'Study task answers and results are not placed inside upstream projects.', '']
    for record in records:
        prompt_lines.extend([f'## {record["folder"]}', '', f'Upstream: {record["source_url"]}', '',
                             '```text', record['task'],
                             'Cite relevant files, functions and test names. If evidence is missing, say so instead of guessing.',
                             '```', '', f'Target for human verification: `{record["target_file"]}` / `{record["target_symbol"]}`.', '',
                             'Define your supported-behavior checklist from source/tests before scoring either answer.', ''])
    (DESTINATION / 'TASKS.md').write_text('\n'.join(prompt_lines) + '\n', encoding='utf-8')
    worksheet = DESTINATION / 'results-template.csv'
    if not worksheet.exists():
        with worksheet.open('x', newline='', encoding='utf-8') as stream:
            writer = csv.writer(stream)
            writer.writerow(['repository', 'folder', 'commit', 'repeat', 'condition', 'model', 'effort',
                             'backend_state', 'correct_supported_facts', 'required_facts',
                             'incorrect_claims', 'unsupported_claims', 'total_answer_seconds',
                             'tokenwise_preparation_seconds', 'observed_tool_calls',
                             'observed_file_read_calls', 'unique_observed_files',
                             'reported_input_tokens', 'reported_output_tokens',
                             'reported_usage_source', 'local_packet_tokens', 'status', 'evidence_path', 'notes'])
            for record in records:
                for repeat in range(1, 4):
                    conditions = ('without', 'with') if repeat != 2 else ('with', 'without')
                    for condition in conditions:
                        writer.writerow([record['repository'], record['folder'], record['commit'], repeat, condition,
                                         *([''] * 12), 'N/A', 'N/A', '', '', 'not_run', '', ''])
    print(f'Prepared twenty projects in {DESTINATION}; no project code or live model calls executed.')


if __name__ == '__main__':
    main()
