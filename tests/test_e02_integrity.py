from pathlib import Path
import hashlib
r=Path(__file__).resolve().parents[1]; a=r/'skills/dcvlog'
required=['SKILL.md','references/opening-ending.md','references/collage-engine.md','references/creative-engine-e02.md','references/delivery-checklist-e02.md','tools/case_catalog.py','tools/telemetry.py','tools/review_upload.py','tools/check_update.py','references/corpus/catalog.json']
for name in required:
 assert (r/name).is_file() and (a/name).is_file(),name
 assert (r/name).read_bytes()==(a/name).read_bytes(),name
BASELINE_SHA256={'tools/telemetry.py': 'c9da9dd2541b278bbf2638c38b4db69246535a561dbee1b83c0ff79325e90cf8', 'tools/review_upload.py': '40303104b08a18378e02d48fec040634f12a2e0915563e287aadb0d838733782', 'references/collage-engine.md': 'f9c5ba6b50dca118daae3fb785a5fea4d8417c4da42e047616470f896b6abfd2', 'references/corpus/batch-003-raw-20261016/cases.md': '4e0edfafe1adfa894213b7cbbe7778a46d67e5525e79fc8afaa3386336dbf067'}
for name in ['tools/telemetry.py','tools/review_upload.py','references/collage-engine.md','references/corpus/batch-003-raw-20261016/cases.md']:
 assert hashlib.sha256((r/name).read_bytes()).hexdigest() == BASELINE_SHA256[name],f"changed protected file {name}"
print('E0.2 protected modules, corpus hashes and mirror: PASS')
