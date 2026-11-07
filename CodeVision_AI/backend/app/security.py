"""Conservative input guardrails. Source code is analyzed as data, never executed."""
from __future__ import annotations
import io
import re
import zipfile
from pathlib import PurePosixPath
from typing import NamedTuple

MAX_ARCHIVE_SIZE = 12 * 1024 * 1024
MAX_FILES = 160
MAX_UNCOMPRESSED_TOTAL = 5 * 1024 * 1024
MAX_FILE_SIZE = 160 * 1024
ALLOWED_EXTENSIONS = {'.py', '.js', '.jsx', '.ts', '.tsx', '.json', '.md', '.toml', '.yaml', '.yml'}
IGNORE_PARTS = {'.git', 'node_modules', '.next', 'dist', 'build', '__pycache__', 'vendor', '.venv', 'venv', 'coverage'}
SECRET_NAMES = {'.env', '.npmrc', '.pypirc', 'credentials.json', 'secrets.json', 'id_rsa'}

class InputError(ValueError):
    pass

class SourceFile(NamedTuple):
    path: str
    text: str

def read_archive(raw: bytes) -> list[SourceFile]:
    if len(raw) > MAX_ARCHIVE_SIZE:
        raise InputError('ZIP is too large (12 MB maximum).')
    try:
        archive = zipfile.ZipFile(io.BytesIO(raw))
    except (zipfile.BadZipFile, ValueError) as exc:
        raise InputError('Upload a valid ZIP repository.') from exc
    found: list[SourceFile] = []
    total = 0
    with archive:
        for item in archive.infolist():
            if item.is_dir():
                continue
            name = item.filename.replace('\\', '/')
            p = PurePosixPath(name)
            if p.is_absolute() or '..' in p.parts or not p.parts or name.startswith('/'):
                raise InputError('Unsafe archive path detected.')
            if (item.external_attr >> 16) & 0o170000 == 0o120000:
                continue  # symlinks
            # Strip one usual GitHub archive root folder in the final phase.
            if any(part in IGNORE_PARTS for part in p.parts):
                continue
            if p.name.lower() in SECRET_NAMES or p.name.startswith('.env'):
                continue
            if p.suffix.lower() not in ALLOWED_EXTENSIONS:
                continue
            if item.file_size > MAX_FILE_SIZE:
                continue
            total += item.file_size
            if total > MAX_UNCOMPRESSED_TOTAL:
                raise InputError('Source exceeds the 5 MB extracted text limit.')
            if len(found) >= MAX_FILES:
                raise InputError(f'Limit is {MAX_FILES} supported files per repository.')
            with archive.open(item) as handle:
                content = handle.read(MAX_FILE_SIZE + 1)
            if len(content) > MAX_FILE_SIZE:
                continue
            if b'\0' in content:
                continue
            text = content.decode('utf-8', errors='replace')
            # Minimal heuristic to prevent accidental secret disclosure to hosted models.
            if re.search(r'(?im)^\s*(?:api_key|secret_key|password|private_key)\s*[:=]\s*[\"\']?[a-z0-9_\-/+]{24,}', text):
                text = re.sub(r'(?im)^(\s*(?:api_key|secret_key|password|private_key)\s*[:=]).*$', r'\1 [REDACTED]', text)
            found.append(SourceFile(path=name, text=text))
    if not found:
        raise InputError('ZIP contains no supported source files.')
    roots = {PurePosixPath(f.path).parts[0] for f in found if len(PurePosixPath(f.path).parts) > 1}
    if len(roots) == 1 and all(len(PurePosixPath(f.path).parts) > 1 for f in found):
        found = [SourceFile('/'.join(PurePosixPath(f.path).parts[1:]), f.text) for f in found]
    return found

GITHUB_RE = re.compile(r'^https://github\.com/([A-Za-z0-9_.-]{1,100})/([A-Za-z0-9_.-]{1,100})(?:\.git)?/?$')

def parse_github_url(url: str) -> tuple[str, str]:
    m = GITHUB_RE.fullmatch(url.strip())
    if not m:
        raise InputError('Use a public repository URL: https://github.com/owner/repo')
    owner, repo = m.groups()
    repo = repo.removesuffix('.git')
    if owner in {'.', '..'} or repo in {'.', '..'}:
        raise InputError('Invalid GitHub repository path.')
    return owner, repo
