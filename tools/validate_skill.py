from pathlib import Path
import re, sys
root = Path(__file__).resolve().parents[1]
skill = root / 'skills' / 'dcvlog' / 'SKILL.md'
text = skill.read_text(encoding='utf-8')
errors=[]
for token in ['name: dcvlog','version: "1.5.1"','author: "daichuan-ai"','/dcvlog','场景 / 用途','成熟样本','90%—110%','service_client_total','video_client_total']:
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
interview=(skill.parent/'references'/'interview-engine.md').read_text(encoding='utf-8')
opening=(skill.parent/'references'/'opening-ending.md').read_text(encoding='utf-8')
for token in ['禁止再问“这个客人大概什么情况','直接进入第3节的5个切口选择']:
    if token not in interview:
        errors.append(f'interview missing {token}')
for token in ['化妆师主角型Vlog开头','（视频原声）','人设尾巴预设库','最多给2个版本']:
    if token not in opening:
        errors.append(f'opening-ending missing {token}')
if errors:
    print('FAIL')
    print('\n'.join(errors))
    sys.exit(1)
print('PASS')
print(f'references={len(actual)}')
print('version=1.5.1')
