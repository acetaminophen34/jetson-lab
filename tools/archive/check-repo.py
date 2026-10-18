#!/usr/bin/env python3
"""Offline checks for documentation links, syntax, immutable assets and publishable Git trees."""
import ast
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
ROOT_FILES = {'README.md', 'LICENSE', '.gitignore', '.gitattributes'}
PREFIXES = {'docs', 'src', 'scripts', 'patches', 'reference', 'licenses'}
EXTENSIONS = {'.md', '.json', '.sh', '.py', '.patch', '.h', '.hpp'}
SECRET = re.compile(r'(?:-----BEGIN [A-Z ]*PRIVATE KEY-----|(?:ghp_|github_pat_|hf_)[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9]{20,}|https?://[^/\s:@]+:[^/\s@]+@|/(?:Users)/[^/\s]+|/(?:home)/(?:a62ss)|192\.168\.[0-9]+\.[0-9]+)')
SECRET_LITERAL = re.compile(r"(?i)\b(?:password|passwd|api[_-]?key|access[_-]?token|secret)[\"']?\s*[:=]\s*[\"'][^\"'\n]{8,}[\"']")
LIMIT = 250000
errors = []


def allowed(name):
    path = Path(name)
    return (name in ROOT_FILES or (path.parts[0] in PREFIXES and (path.suffix in EXTENSIONS or (path.parts[0] == 'licenses' and path.name.endswith('LICENSE'))))) and not any(
        v in path.parts for v in ['private', 'backups', 'models', 'build', '__pycache__'])


def inspect(name, data):
    if not allowed(name):
        errors.append('Not allowlisted: ' + name)
    if len(data) > LIMIT:
        errors.append('Oversized public file: ' + name)
        return
    try:
        text = data.decode('utf8')
    except UnicodeError:
        errors.append('Non-text public file: ' + name)
        return
    if SECRET.search(text) or SECRET_LITERAL.search(text):
        errors.append('Sensitive literal pattern: ' + name)


def slug(text):
    return ''.join(c for c in re.sub(r'[`*_]', '', text.lower()) if c.isalnum() or c in '-_ ').replace(' ', '-')


def anchors(path):
    text = re.sub(r'^```.*?^```[^\n]*$', '', path.read_text(), flags=re.M | re.S)
    result = set()
    counts = {}
    for heading in re.findall(r'^#{1,6}\s+(.+)$', text, re.M):
        base = slug(heading)
        count = counts.get(base, 0)
        result.add(base if count == 0 else base + '-' + str(count))
        counts[base] = count + 1
    return result


def git(*args):
    return subprocess.check_output(['git', '-C', str(ROOT)] + list(args))


files = [p for p in ROOT.rglob('*') if '.git' not in p.relative_to(ROOT).parts and p.is_file()]
shell_count = 0
for path in files:
    name = str(path.relative_to(ROOT))
    if path.is_symlink():
        errors.append('Symlink forbidden: ' + name)
        continue
    data = path.read_bytes()
    inspect(name, data)
    if path.suffix == '.py':
        try:
            try:
                ast.parse(data.decode(), filename=name, feature_version=(3, 6))
            except TypeError:  # Python 3.6 uses its own grammar.
                ast.parse(data.decode(), filename=name)
        except (SyntaxError, ValueError) as exc:
            errors.append('Python syntax: {}: {}'.format(name, exc))
    if path.suffix == '.sh':
        check = subprocess.run(['bash', '-n', str(path)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if check.returncode:
            errors.append('Shell syntax: ' + name + ': ' + check.stderr.decode())
    if path.suffix != '.md':
        continue
    text = path.read_text()
    for target in re.findall(r'\]\(([^)]+)\)', text):
        if re.match(r'[A-Za-z][A-Za-z0-9+.-]*:', target):
            continue
        relative, _, fragment = unquote(target).partition('#')
        dest = (path.parent / relative).resolve() if relative else path
        if not dest.is_file() or (dest != ROOT and ROOT not in dest.parents):
            errors.append('Broken/escaping link: {} -> {}'.format(name, target))
        elif fragment and dest.suffix == '.md' and fragment not in anchors(dest):
            errors.append('Broken anchor: {} -> {}'.format(name, target))
    for block in re.findall(r'^```(?:sh|bash)\n(.*?)^```', text, re.M | re.S):
        shell_count += 1
        check = subprocess.run(['bash', '-n'], input=block.encode(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if check.returncode:
            errors.append('Markdown shell syntax: {}: {}'.format(name, check.stderr.decode()))

for asset in json.loads((ROOT / 'reference/asset-manifest.json').read_text()):
    path = ROOT / asset['path']
    if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != asset['sha256']:
        errors.append('Original asset hash mismatch: ' + asset['path'])

# Original copied code is immutable apart from the recorded privacy transformation.
origins_path = ROOT / 'reference/code-origins.json'
if origins_path.exists():
    for record in json.loads(origins_path.read_text())['entries']:
        path = ROOT / record['public_path']
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != record['public_sha256']:
            errors.append('Source provenance hash mismatch: ' + record['public_path'])
        if record['preservation'] == 'verbatim' and record['original_sha256'] != record['public_sha256']:
            errors.append('Unrecorded source modification: ' + record['public_path'])

commits = []
if (ROOT / '.git').exists():
    commits = git('rev-list', '--all').decode().splitlines()
    blobs = set()
    for commit in commits:
        for item in git('ls-tree', '-r', '-l', '-z', commit).split(b'\0'):
            if not item:
                continue
            meta, raw_name = item.split(b'\t', 1)
            mode, kind, oid, size = meta.decode().split()
            name = raw_name.decode()
            if mode == '120000' or kind != 'blob' or not allowed(name) or int(size) > LIMIT:
                errors.append('Disallowed Git history entry: ' + name)
                continue
            if oid not in blobs:
                inspect(name, git('cat-file', 'blob', oid))
                blobs.add(oid)
    # The staged tree must be safe before an initial commit as well.
    for entry in git('ls-files', '--stage', '-z').decode().split('\0'):
        if not entry:
            continue
        meta, name = entry.split('\t', 1)
        mode, oid, stage = meta.split()
        if mode not in {'100644', '100755'} or stage != '0':
            errors.append('Disallowed index mode/stage: ' + name)
            continue
        try:
            inspect(name, git('show', ':' + name))
        except subprocess.CalledProcessError:
            errors.append('Cannot read index entry: ' + name)

if errors:
    for error in errors:
        print('FAIL: ' + error, file=sys.stderr)
    raise SystemExit(1)
print('PASS: {} files, {} shell blocks, {} Git commits; links/assets/publication checks'.format(
    len(files), shell_count, len(commits)))
