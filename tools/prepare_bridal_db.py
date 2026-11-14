"""Locate or temporarily fetch original DB modules. Preparation is NOT execution.

Python stdlib with an optional system curl fallback. No credentials, uploads or installation.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import tempfile
import urllib.request
import urllib.error
from urllib.parse import urlparse

REPO = 'dontbesilent2025/dbskill'
DEFAULT = ('dbs-script-flow', 'dbs-title-cover-intro')
ALLOWED = {*DEFAULT, 'dbs-resonate'}
HOSTS = {'api.github.com', 'raw.githubusercontent.com', 'github.com'}
LIMIT = 2 * 1024 * 1024


_prefer_curl = False


def checked_response(url, data, limit):
    dest = urlparse(url)
    if dest.scheme != 'https' or dest.hostname not in HOSTS:
        raise ValueError('Unexpected source destination')
    if len(data) > limit:
        raise ValueError('Source exceeds size limit')
    return data


def curl_get(url, limit):
    executable = shutil.which('curl')
    if not executable:
        raise OSError('Python source download failed and curl is unavailable')
    try:
        result = subprocess.run(
            [executable, '--fail', '--silent', '--show-error', '--location',
             '--max-redirs', '4', '--proto', '=https', '--proto-redir', '=https',
             '--max-time', '20', '--max-filesize', str(limit + 1),
             '--user-agent', 'DCVlog-DB-Loader', '--write-out', '\n%{url_effective}', url],
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, timeout=25, check=False)
    except subprocess.TimeoutExpired as exc:
        raise OSError('Official source download timed out') from exc
    if result.returncode:
        raise OSError('Official source download failed')
    data, sep, effective = result.stdout.rpartition(b'\n')
    if not sep:
        raise ValueError('Missing source destination verification')
    return checked_response(effective.decode('utf-8'), data, limit)


def get(url, limit=LIMIT):
    global _prefer_curl
    checked_response(url, b'', limit)
    if _prefer_curl:
        return curl_get(url, limit)
    request = urllib.request.Request(url, headers={'User-Agent': 'DCVlog-DB-Loader'})
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            return checked_response(response.geturl(), response.read(limit + 1), limit)
    except urllib.error.HTTPError:
        raise
    except (urllib.error.URLError, TimeoutError):
        data = curl_get(url, limit)
        # Reuse the working transport for this preparation only. No system changes.
        _prefer_curl = True
        return data


def identity(path, name):
    if not path.is_file() or path.stat().st_size > LIMIT:
        return False
    body = path.read_text(encoding='utf-8')
    front = body.split('---', 2)
    return len(front) == 3 and body.startswith('---\n') and bool(
        re.search(r'^name:\s*[\"\']?' + re.escape(name) + r'[\"\']?\s*$', front[1], re.M))


def module_dir(root, name):
    for base in (root / name, root / 'skills' / name, root):
        if identity(base / 'SKILL.md', name):
            return base.resolve()
    return None


def describe(base, name, origin, revision=None):
    resources = []
    for path in sorted(base.rglob('*')):
        if not path.is_file() or path.is_symlink() or '__pycache__' in path.parts:
            continue
        if path.suffix in {'.pyc', '.pyo'} or '.git' in path.parts:
            continue
        if path.stat().st_size > LIMIT:
            raise ValueError('Installed resource exceeds size limit')
        resources.append({'relative_path': path.relative_to(base).as_posix(),
                          'path': str(path),
                          'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
        if len(resources) > 250:
            raise ValueError('Module contains too many resources')
    return {'name': name, 'origin': origin, 'revision': revision,
            'entrypoint': str(base / 'SKILL.md'), 'resources': resources}


def roots(explicit=None):
    if explicit is not None:
        return [Path(explicit).expanduser().resolve()]
    home = Path.home()
    candidates = [Path(__file__).resolve().parents[2], Path.cwd() / '.agents/skills',
                  Path.cwd() / '.codebuddy/skills', Path.cwd() / '.workbuddy/skills',
                  home / '.agents/skills', home / '.codebuddy/skills',
                  home / '.workbuddy/skills', home / '.claude/skills',
                  home / '.codex/skills']
    return list(dict.fromkeys(p.resolve() for p in candidates))


def fetch_modules(names):
    tree = json.loads(get('https://api.github.com/repos/' + REPO + '/git/trees/main?recursive=1',
                          8 * LIMIT))
    revision = tree.get('sha', '')
    if not re.fullmatch(r'[0-9a-f]{40}', revision) or tree.get('truncated'):
        raise ValueError('Cannot verify complete official tree and revision')
    entries = tree.get('tree', [])
    selected = []
    for item in entries:
        name = item.get('path', '')
        path = PurePosixPath(name)
        if len(path.parts) < 3 or path.parts[0] != 'skills' or path.parts[1] not in names:
            continue
        if path.is_absolute() or '..' in path.parts or '\\' in name:
            raise ValueError('Unsafe official resource path')
        if item.get('type') != 'blob':
            continue
        if item.get('mode') not in {'100644', '100755'}:
            raise ValueError('Unsupported resource type')
        if item.get('size', LIMIT + 1) > LIMIT:
            raise ValueError('Official resource exceeds size limit')
        selected.append(item)
    if len(selected) > 250 or sum(x['size'] for x in selected) > 12 * LIMIT:
        raise ValueError('Selected modules exceed size limit')
    for name in names:
        if not any(x['path'] == 'skills/' + name + '/SKILL.md' for x in selected):
            raise ValueError('Official module is missing: ' + name)
    dest = Path(tempfile.mkdtemp(prefix='dcvlog-db-'))
    # Keep original paths so local references resolve without rewriting source.
    def download(item):
        data = get('https://raw.githubusercontent.com/' + REPO + '/' + revision + '/' + item['path'])
        blob = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
        if blob != item['sha']:
            raise ValueError('Official blob verification failed: ' + item['path'])
        path = dest / item['path']
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    with ThreadPoolExecutor(max_workers=4) as pool:
        list(pool.map(download, selected))
    out = []
    for name in names:
        base = dest / 'skills' / name
        if not identity(base / 'SKILL.md', name):
            raise ValueError('Official module identity mismatch')
        out.append(describe(base, name, 'official-github-temporary', revision))
    return out


def prepare(names=DEFAULT, installed_root=None, offline=False):
    if not names or any(name not in ALLOWED for name in names):
        raise ValueError('Unsupported DB module requested')
    found, missing = [], []
    locations = roots(installed_root)
    for name in dict.fromkeys(names):
        match = next((p for root in locations if (p := module_dir(root, name))), None)
        if match:
            found.append(describe(match, name, 'installed'))
        else:
            missing.append(name)
    if missing:
        if offline:
            raise ValueError('Required installed DB module unavailable: ' + ', '.join(missing))
        found.extend(fetch_modules(missing))
    order = {name: i for i, name in enumerate(names)}
    return {'status': 'prepared_not_executed', 'executed': False, 'repository': REPO,
            'modules': sorted(found, key=lambda x: order[x['name']]),
            'next': 'Read full entrypoints and required resources; execute DB workflow on the actual draft; return the revised middle draft.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--module', action='append', choices=sorted(ALLOWED))
    parser.add_argument('--installed-root')
    parser.add_argument('--offline', action='store_true')
    args = parser.parse_args()
    try:
        result = prepare(tuple(args.module or DEFAULT), args.installed_root, args.offline)
    except (ValueError, OSError, KeyError, TypeError) as error:
        print(json.dumps({'status': 'unavailable', 'executed': False, 'error': str(error)}, ensure_ascii=False))
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
