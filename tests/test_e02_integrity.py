from pathlib import Path
import hashlib
r=Path(__file__).resolve().parents[1]; a=r/'skills/dcvlog'
required=['SKILL.md','references/opening-ending.md','references/creative-engine-e02.md','references/delivery-checklist-e02.md','tools/case_catalog.py','tools/telemetry.py','tools/review_upload.py','tools/check_update.py','tools/update_skill.py','references/corpus/catalog.json']
for name in required:
 assert (r/name).is_file() and (a/name).is_file(),name
 assert (r/name).read_bytes()==(a/name).read_bytes(),name
BASELINE_SHA256={'tools/review_upload.py': '9b6ac7b480b31ed753d95cb14720b8b859989d4a696dbac100a10dec8f0700c9', 'references/corpus/batch-003-raw-20261016/cases.md': '4e0edfafe1adfa894213b7cbbe7778a46d67e5525e79fc8afaa3386336dbf067'}
for name in ['tools/review_upload.py','references/corpus/batch-003-raw-20261016/cases.md']:
 assert hashlib.sha256((r/name).read_bytes()).hexdigest() == BASELINE_SHA256[name],f"changed protected file {name}"
print('E0.2 protected modules, corpus hashes and mirror: PASS')
