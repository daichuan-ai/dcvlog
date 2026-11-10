"""Check local creative-stage artifacts; never claims to judge writing quality."""
import argparse
import json
from pathlib import Path
import re


def text(value):
    return isinstance(value, str) and bool(value.strip())


def compact(value):
    return re.sub(r"\s+", "", value)


def check(record):
    def fail(stage, reason):
        return {"ready": False, "return_to": stage, "reason": reason,
                "scope": "artifact_integrity_only"}

    if not isinstance(record, dict) or not text(record.get("rough_draft")):
        return fail("ROUGH_DRAFT", "缺少完整事实粗稿")
    plan = record.get("emotion_plan", {})
    if not isinstance(plan, dict) or not all(text(plan.get(k)) for k in ("center_judgment", "audience", "ending_response")):
        return fail("EMOTION_PLAN", "缺少中心判断、共鸣人群或作者结尾回应")
    progression = plan.get("progression", [])
    if not isinstance(progression, list) or not progression or not all(
            isinstance(p, dict) and all(text(p.get(k)) for k in ("fact", "response", "serves_center")) for p in progression):
        return fail("EMOTION_PLAN", "缺少事实到感受再到中心的推进记录")
    if not text(record.get("body_draft")):
        return fail("BODY_DRAFT", "缺少DB实际创作的正文")
    brief = record.get("opening_brief", {})
    if not isinstance(brief, dict) or not all(text(brief.get(k)) for k in ("core_judgment", "audience", "tension", "viewer_question")) or not isinstance(brief.get("fact_anchors"), list) or not brief["fact_anchors"] or not all(text(p) for p in brief["fact_anchors"]):
        return fail("OPENING_BRIEF", "缺少独立开头创作简报")
    candidates = record.get("opening_candidates", [])
    keys = ("id", "mechanism", "hook", "next_line", "first_shot", "reason")
    if not isinstance(candidates, list) or len(candidates) < 2 or not all(
            isinstance(c, dict) and all(text(c.get(k)) for k in keys) for c in candidates):
        return fail("OPENING_CANDIDATES", "至少两个有范式、开头、承接句与画面的候选")
    if len({c["id"] for c in candidates}) != len(candidates) or len({c["mechanism"] for c in candidates}) < 2 or len({compact(c["hook"]) for c in candidates}) != len(candidates):
        return fail("OPENING_CANDIDATES", "候选编号、范式或开头没有形成不同选择")
    selected = next((c for c in candidates if c["id"] == record.get("opening_choice")), None)
    if not selected:
        return fail("OPENING_CHOICE", "尚无有效的用户开头选择或已授权代选")
    assembled = record.get("assembled", {})
    if not isinstance(assembled, dict) or not text(assembled.get("script")):
        return fail("ASSEMBLED", "缺少装入所选开头的完整稿")
    script = assembled["script"]
    if not compact(script).startswith(compact(selected["hook"] + selected["next_line"])):
        return fail("ASSEMBLED", "完整稿未从所选开头和承接句开始")
    evidence = assembled.get("emotion_evidence", [])
    if not isinstance(evidence, list) or not evidence or not all(text(q) and q in script for q in evidence):
        return fail("BODY_DRAFT", "作者感受摘句缺失或不在实际全文中")
    ending = assembled.get("ending_response")
    if not text(ending) or not script.rstrip().endswith(ending.strip()):
        return fail("EMOTION_PLAN", "结尾没有实际装入作者情感回应")
    promise = assembled.get("promise_evidence")
    if not text(promise) or promise not in script:
        return fail("ASSEMBLED", "缺少开头承诺在正文中的实际承接摘句")
    return {"ready": True, "return_to": None, "scope": "artifact_integrity_only",
            "writing_quality_verified": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("record", type=Path)
    args = parser.parse_args()
    try:
        result = check(json.loads(args.record.read_text(encoding="utf-8")))
    except (OSError, ValueError) as exc:
        result = {"ready": False, "return_to": "RECORD", "reason": str(exc),
                  "scope": "artifact_integrity_only"}
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result["ready"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
