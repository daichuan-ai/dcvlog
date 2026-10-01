from pathlib import Path
import re, sys
root = Path(__file__).resolve().parents[1]
skill = root / 'skills' / 'dcvlog' / 'SKILL.md'
text = skill.read_text(encoding='utf-8')
errors=[]
for token in ['name: dcvlog','version: "1.3.1"','author: "daichuan-ai"','/dcvlog']:
    if token not in text: errors.append(f'missing {token}')
refs = re.findall(r'@references/([A-Za-z0-9_.-]+)', text)
for ref in sorted(set(refs)):
    if not (skill.parent/'references'/ref).exists(): errors.append(f'missing ref {ref}')
actual = list((skill.parent/'references').glob('*.md'))
if len(actual) != 6: errors.append(f'expected 6 refs, got {len(actual)}')
if errors:
    print('FAIL')
    print('\n'.join(errors))
    sys.exit(1)
print('PASS')
print(f'references={len(actual)}')
print('version=1.3.1')
