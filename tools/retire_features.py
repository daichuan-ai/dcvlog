"""Remove fixed retired feature files from the active Skill, retaining a backup."""
import argparse
import datetime
import json
from pathlib import Path
import re
import shutil
import uuid

RETIRED = ('references/collage-engine.md',)


def retire(skill_dir):
    root = Path(skill_dir).expanduser().resolve(strict=True)
    text = (root / 'SKILL.md').read_text(encoding='utf-8')
    front = text.split('---', 2)
    if len(front) != 3 or not re.search(r'^name:\s*dcvlog\s*$', front[1], re.M):
        raise ValueError('Not a DCVlog installation')
    version = (root / 'VERSION').read_text().strip()
    if not re.fullmatch(r'\d+\.\d+\.\d+', version) or tuple(map(int, version.split('.'))) < (2, 0, 0):
        raise ValueError('Retirement requires DCVlog 2.0.0 or newer')
    existing = []
    for relative in RETIRED:
        path = root
        for part in Path(relative).parts:
            path /= part
            if path.is_symlink():
                raise ValueError('Retired path contains a symbolic link')
        if path.exists():
            if not path.is_file():
                raise ValueError('Retired path is not a file')
            existing.append((relative, path))
    backup = None
    if existing:
        parent = root.parent / ('.' + root.name + '.dcvlog-backups')
        if parent.is_symlink():
            raise ValueError('Backup directory is a symbolic link')
        stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
        backup = parent / ('retired-' + stamp + '-' + uuid.uuid4().hex[:8])
        for relative, path in existing:
            destination = backup / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, destination)
        for _, path in existing:
            path.unlink()
    return {'status': 'retired' if existing else 'clean', 'skill_dir': str(root),
            'removed': [relative for relative, _ in existing],
            'backup_path': str(backup) if backup else None}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--skill-dir', required=True)
    args = parser.parse_args()
    try:
        result = retire(args.skill_dir)
    except (ValueError, OSError) as error:
        print(json.dumps({'status': 'unavailable', 'error': str(error)}, ensure_ascii=False))
        return 1
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
