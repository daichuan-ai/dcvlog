from pathlib import Path
import re, sys
root = Path(__file__).resolve().parents[1]
skill = root / 'skills' / 'dcvlog' / 'SKILL.md'
text = skill.read_text(encoding='utf-8')
errors=[]
for token in ['name: dcvlog','version: "1.5.0"','author: "daichuan-ai"','/dcvlog','场景 / 用途','成熟样本','90%—110%']:
    if token not in text:
        errors.append(f'missing {token}')
refs = re.findall(r'@references/([A-Za-z0-9_.-]+)', text)
for ref in sorted(set(refs)):
    if not (skill.parent/'references'/ref).exists():
        errors.append(f'missing ref {ref}')
actual = list((skill.parent/'references').glob('*.md'))
if len(actual) != 6:
    errors.append(f'expected 6 refs, got {len(actual)}')
for required in ['makeup-corpus.md','writing-style.md','interview-engine.md']:
    rt=(skill.parent/'references'/required).read_text(encoding='utf-8')
    if '场景' not in rt:
        errors.append(f'{required} missing scenario/service layer')
for required in ['makeup-corpus.md','writing-style.md']:
    rt=(skill.parent/'references'/required).read_text(encoding='utf-8')
    if '长度' not in rt:
        errors.append(f'{required} missing mature length calibration')
if errors:
    print('FAIL')
    print('\n'.join(errors))
    sys.exit(1)
print('PASS')
print(f'references={len(actual)}')
print('version=1.5.0')
