from pathlib import Path
import re, sys
root = Path(__file__).resolve().parents[1]
skill = root / 'skills' / 'dcvlog' / 'SKILL.md'
text = skill.read_text(encoding='utf-8')
errors=[]
for rel in ['skills/dcvlog/tools/telemetry.py','skills/dcvlog/telemetry-config.json','docs/ANALYTICS_SETUP.md']:
    if not (root/rel).exists():
        errors.append(f'missing telemetry file {rel}')
for token in ['name: dcvlog','version: "1.8.1"','author: "daichuan-ai"','/dcvlog','我要开始写文案','我要做拼图','更新 DCVlog','加入 DCVlog 新案例库','扫描新案例库，升级当前方法','场景 / 用途','成熟样本','90%—110%','service_client_total','video_client_total','第1个讲故事','40秒','collage-engine.md','代川很乐意帮你完成','代川来陪你把今天这条捋出来','corpus/corpus-index.md','corpus/current-patterns.md','dcvlog_open','write_vlog_start','write_vlog_complete','collage_start','collage_complete','匿名使用统计']:
    if token not in text:
        errors.append(f'missing {token}')
# top-level runtime refs remain 7 for compatibility
actual = list((skill.parent/'references').glob('*.md'))
if len(actual) != 7:
    errors.append(f'expected 7 top-level refs, got {len(actual)}')
for required in ['makeup-corpus.md','writing-style.md','interview-engine.md']:
    rt=(skill.parent/'references'/required).read_text(encoding='utf-8')
    if '场景' not in rt:
        errors.append(f'{required} missing scenario/service layer')
for required in ['makeup-corpus.md','writing-style.md']:
    rt=(skill.parent/'references'/required).read_text(encoding='utf-8')
    if '长度' not in rt:
        errors.append(f'{required} missing mature length calibration')
writing=(skill.parent/'references'/'writing-style.md').read_text(encoding='utf-8')
for token in ['第1个讲故事，第2个讲重点，第3个以后看结果','不再套单客40秒上限','总长度随客人数增加','corpus/corpus-index.md','corpus/current-patterns.md']:
    if token not in writing:
        errors.append(f'writing-style missing {token}')
interview=(skill.parent/'references'/'interview-engine.md').read_text(encoding='utf-8')
opening=(skill.parent/'references'/'opening-ending.md').read_text(encoding='utf-8')
for token in ['禁止再问“这个客人大概什么情况','直接进入第3节的5个切口选择']:
    if token not in interview:
        errors.append(f'interview missing {token}')
for token in ['化妆师主角型Vlog开头','（视频原声）','人设尾巴预设库','最多给2个版本']:
    if token not in opening:
        errors.append(f'opening-ending missing {token}')
collage=(skill.parent/'references'/'collage-engine.md').read_text(encoding='utf-8')
for token in ['1—6张','3:4','自动选主图','禁止默认做普通2×2宫格','原图保护','韩系英文标题库','换一版','❓这组照片你想怎么出图？','每张照片分别做一张独立作品页','两种都要','N + 1','工作室名字','签名名字','英文 / 拼音','已有的拉丁字母品牌词原样保留','陈述句、确认句、说明句前禁止加 `❓`']:
    if token not in collage:
        errors.append(f'collage-engine missing {token}')
corpus_root=skill.parent/'references'/'corpus'
for rel in ['CORPUS_VERSION','corpus-index.md','current-patterns.md','batch-001-baseline/cases.md','batch-002-new/README.md']:
    if not (corpus_root/rel).exists():
        errors.append(f'missing corpus file {rel}')
if (corpus_root/'CORPUS_VERSION').exists() and (corpus_root/'CORPUS_VERSION').read_text(encoding='utf-8').strip() != '1.0.0':
    errors.append('unexpected corpus version')
if (corpus_root/'corpus-index.md').exists():
    ci=(corpus_root/'corpus-index.md').read_text(encoding='utf-8')
    for token in ['Batch 001','LOCKED','Batch 002','OPEN','加入 DCVlog 新案例库','扫描新案例库，升级当前方法']:
        if token not in ci:
            errors.append(f'corpus-index missing {token}')
if errors:
    print('FAIL')
    print('\n'.join(errors))
    sys.exit(1)
print('PASS')
print(f'top_level_references={len(actual)}')
print('version=1.8.1')
print('corpus_version=1.0.0')
