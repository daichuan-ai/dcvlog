from pathlib import Path
import hashlib, re, sys
root = Path(__file__).resolve().parents[1]
skill = root / 'skills' / 'dcvlog' / 'SKILL.md'
text = skill.read_text(encoding='utf-8')
errors=[]
for rel in ['skills/dcvlog/tools/telemetry.py','skills/dcvlog/telemetry-config.json','docs/ANALYTICS_SETUP.md',
            'skills/dcvlog/tools/review_upload.py','skills/dcvlog/review-config.json',
            'skills/dcvlog/references/review-collection.md','docs/REVIEW_PILOT_SETUP.md',
            'cloudbase/review-collector/index.js','cloudbase/review-collector/schema.sql',
            'cloudbase/review-collector/package.json']:
    if not (root/rel).exists():
        errors.append(f'missing telemetry file {rel}')
for token in ['name: dcvlog','version: "1.9.2"','author: "daichuan-ai"','/dcvlog','我要开始写文案','我要做拼图','更新 DCVlog','加入 DCVlog 新案例库','扫描新案例库，升级当前方法','场景 / 用途','成熟样本','90%—110%','service_client_total','video_client_total','第1个讲故事','40秒','collage-engine.md','aesthetic-interview.md','visual-result-draft-gate.md','post-makeup-commentary.md','version-check.md','review-collection.md','review_upload.py','首次同意','LIGHT_READY','tools/check_update.py','静默查新','妆后照片和视频','batch-003-raw-20261016','代川很乐意帮你完成','代川来陪你把今天这条捋出来','corpus/corpus-index.md','corpus/current-patterns.md','dcvlog_open','write_vlog_start','write_vlog_complete','collage_start','collage_complete','匿名使用统计','NEED_ASK','READY','LIMITED_DRAFT','可能第一次','参考图','拍照妥妥够用']:
    if token not in text:
        errors.append(f'missing {token}')
# 累计12个运行参考；V1.8.6原有11个文件必须全部保留
actual = list((skill.parent/'references').glob('*.md'))
if len(actual) < 12:
    errors.append(f'expected at least 12 top-level refs, got {len(actual)}')
for required in ['makeup-corpus.md','writing-style.md','interview-engine.md']:
    rt=(skill.parent/'references'/required).read_text(encoding='utf-8')
    if '场景' not in rt:
        errors.append(f'{required} missing scenario/service layer')
for required in ['makeup-corpus.md','writing-style.md']:
    rt=(skill.parent/'references'/required).read_text(encoding='utf-8')
    if '长度' not in rt:
        errors.append(f'{required} missing mature length calibration')
writing=(skill.parent/'references'/'writing-style.md').read_text(encoding='utf-8')
for token in ['第1位解读作品，第2位讲重点，第3/4位带作品','不再套单客40秒上限','总长度随客人数增加','corpus/corpus-index.md','corpus/current-patterns.md']:
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
for token in ['1—6张','3:4','自动选主图','禁止默认做普通2×2宫格','原图保护','韩系英文标题库','换一版','❓这组照片你想怎么出图？','每张照片分别做一张独立作品页','两种都要','N + 1','工作室名字','签名名字','英文 / 拼音','已有的拉丁字母品牌词原样保留','陈述句、确认句、说明句前禁止加 `❓`','任何缩放必须等比','细节裁剪必须有明确视觉中心','半个额头','半只眼睛','版式服务照片']:
    if token not in collage:
        errors.append(f'collage-engine missing {token}')
corpus_root=skill.parent/'references'/'corpus'
for rel in ['CORPUS_VERSION','corpus-index.md','current-patterns.md','batch-001-baseline/cases.md','batch-002-new/README.md','batch-003-raw-20261016/cases.md','batch-003-raw-20261016/selection-guide.md']:
    if not (corpus_root/rel).exists():
        errors.append(f'missing corpus file {rel}')
if (corpus_root/'CORPUS_VERSION').exists() and (corpus_root/'CORPUS_VERSION').read_text(encoding='utf-8').strip() != '1.2.0':
    errors.append('unexpected corpus version')
if (corpus_root/'corpus-index.md').exists():
    ci=(corpus_root/'corpus-index.md').read_text(encoding='utf-8')
    for token in ['Batch 001','LOCKED','Batch 002','OPEN','Batch 003','19条','加入 DCVlog 新案例库','扫描新案例库，升级当前方法']:
        if token not in ci:
            errors.append(f'corpus-index missing {token}')
raw=(corpus_root/'batch-003-raw-20261016'/'cases.md')
if raw.exists():
    count=len(re.findall(r'^## 案例 \d\d$', raw.read_text(encoding='utf-8'), re.M))
    if count != 19:
        errors.append(f'expected 19 original cases, got {count}')
    original_digest='4e0edfafe1adfa894213b7cbbe7778a46d67e5525e79fc8afaa3386336dbf067'
    if hashlib.sha256(raw.read_bytes()).hexdigest() != original_digest:
        errors.append('19-case raw corpus differs from the locked original bytes')
else:
    count=0
gate=(skill.parent/'references'/'aesthetic-interview.md').read_text(encoding='utf-8')
draft_gate=(skill.parent/'references'/'visual-result-draft-gate.md').read_text(encoding='utf-8')
evidence=(skill.parent/'references'/'truth-evidence.md').read_text(encoding='utf-8')
for label, body, tokens in [
    ('aesthetic-interview', gate, ['NEED_ASK','READY','LIMITED_DRAFT','LIGHT_READY','沟通流程','画面描述','实际动作']),
    ('visual-result-draft-gate', draft_gate, ['拍照妥妥够用','可能第一次','指着手机说','逐句证据']),
    ('truth-evidence', evidence, ['不确定','引语边界','参考图','图片'])
]:
    for token in tokens:
        if token not in body:
            errors.append(f'{label} missing regression guard {token}')
if (root/'VERSION').read_text(encoding='utf-8').strip() != '1.9.2':
    errors.append('root VERSION != 1.8.7')
config=(skill.parent/'telemetry-config.json').read_text(encoding='utf-8')
for token in ['"skill_version": "1.9.2"','"corpus_version": "1.2.0"']:
    if token not in config:
        errors.append(f'telemetry config missing {token}')
if not (skill.parent/'tools'/'check_update.py').is_file():
    errors.append('missing packaged check_update.py')
else:
    checker=(skill.parent/'tools'/'check_update.py').read_text(encoding='utf-8')
    for token in ['VERSION_URL','timeout=2.5','update_available','unavailable']:
        if token not in checker:
            errors.append(f'update checker missing {token}')
for ref, tokens in [
    ('post-makeup-commentary.md', ['50/50','妆后照片','妆后视频','设计意图','第3/4位']),
    ('version-check.md', ['/dcvlog','update_available','继续使用','无法']),
    ('review-collection.md', ['同意','不同意','status','submit','LIMITED_DRAFT','默认']),
]:
    body=(skill.parent/'references'/ref).read_text(encoding='utf-8')
    for token in tokens:
        if token not in body:
            errors.append(f'{ref} missing {token}')
if errors:
    print('FAIL')
    print('\n'.join(errors))
    sys.exit(1)
print('PASS')
print(f'top_level_references={len(actual)}')
print(f'raw_cases={count}')
print('version=1.9.2')
print('corpus_version=1.2.0')
print('raw_sha256='+hashlib.sha256(raw.read_bytes()).hexdigest())
