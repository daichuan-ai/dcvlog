from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / "skills" / "dcvlog"
SKILL = SKILL_DIR / "SKILL.md"
text = SKILL.read_text(encoding="utf-8")

required = {
    "name": "dcvlog",
    "version": '"1.0.8"',
    "author": '"daichuan-ai"',
}
for key, value in required.items():
    needle = f"{key}: {value}"
    if needle not in text:
        raise SystemExit(f"FAIL: missing {needle}")

refs = re.findall(r"@references/([A-Za-z0-9._-]+\.md)", text)
missing = [r for r in sorted(set(refs)) if not (SKILL_DIR / "references" / r).exists()]
if missing:
    raise SystemExit("FAIL: missing refs: " + ", ".join(missing))

for bad in ["daichuan-ai/dc-makeup-vlog", "version=1.0.7"]:
    for p in ROOT.rglob("*.md"):
        if bad in p.read_text(encoding="utf-8") and p.name not in {"V1.0.5_TO_V1.0.8_DEVLOG.md", "CHANGELOG.md"}:
            raise SystemExit(f"FAIL: stale identity {bad} in {p}")

print(f"PASS: dcvlog v1.0.8; refs={len(list((SKILL_DIR/'references').glob('*.md')))}")
