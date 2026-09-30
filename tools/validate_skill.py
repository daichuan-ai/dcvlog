from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / "skills" / "dcvlog"
SKILL = SKILL_DIR / "SKILL.md"
text = SKILL.read_text(encoding="utf-8")

required = {
    "name": "dcvlog",
    "version": '"1.2.0"',
    "author": '"daichuan-ai"',
}
for key, value in required.items():
    needle = f"{key}: {value}"
    if needle not in text:
        raise SystemExit(f"FAIL: missing {needle}")

for phrase in [
    "/dcvlog",
    "我先认识一下你。你是哪一年的？",
    "你今天一共几个客人？",
    "目标客户",
    "提问深度",
    "强画面",
    "强情绪",
    "强数字",
    "纯文案钩子",
    "标准镜头",
]:
    if phrase not in text:
        raise SystemExit(f"FAIL: missing behavior marker: {phrase}")

if "好，川导开工" in text:
    raise SystemExit("FAIL: stale developer launch phrase remains")

refs = re.findall(r"@references/([A-Za-z0-9._-]+\.md)", text)
missing = [r for r in sorted(set(refs)) if not (SKILL_DIR / "references" / r).exists()]
if missing:
    raise SystemExit("FAIL: missing refs: " + ", ".join(missing))

for p in ROOT.rglob("*.md"):
    t=p.read_text(encoding="utf-8")
    if "daichuan-ai/dc-makeup-vlog" in t:
        raise SystemExit(f"FAIL: stale repo identity in {p}")
    if 'version=1.0.8' in t and p.name not in {"V1.0.5_TO_V1.2.0_DEVLOG.md", "CHANGELOG.md"}:
        raise SystemExit(f"FAIL: stale version marker in {p}")

print(f"PASS: dcvlog v1.2.0; refs={len(list((SKILL_DIR/'references').glob('*.md')))}")
