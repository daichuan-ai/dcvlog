"""Validate handoff artifacts and review freshness, never prose quality."""
import argparse
import hashlib
import json
from pathlib import Path
import re


def text(value):
    return isinstance(value, str) and bool(value.strip())


def compact(value):
    return re.sub(r"\s+", "", value)


def script_hash(script):
    return hashlib.sha256(script.encode('utf-8')).hexdigest()


def check(record):
    def fail(stage, reason):
        return {'ready': False, 'return_to': stage, 'reason': reason,
                'scope': 'artifact_integrity_only', 'writing_quality_verified': False}

    if not isinstance(record, dict) or not text(record.get('rough_draft')):
        return fail('ROUGH_DRAFT', '缺少事实底稿；复用原采访，不重新提问')
    brief = record.get('story_brief')
    if not isinstance(brief, dict) or not all(text(brief.get(k)) for k in ('event', 'author_point', 'audience')):
        return fail('STORY_BRIEF', '从现有材料与用户选择形成事情、作者表达和观众简报')
    if not text(record.get('author_draft')):
        return fail('AUTHOR_DRAFT', '缺少作者口语创作稿；先从事实写成讲述，再交DB改稿')
    if not text(record.get('body_draft')):
        return fail('BODY_DRAFT', '缺少完整创作稿')
    db = record.get('db_execution')
    if not isinstance(db, dict) or not text(db.get('source')) or not isinstance(db.get('modules'), list) or not db['modules'] or not all(text(m) for m in db['modules']):
        return fail('DB_EXECUTION', '缺少DB来源与模块记录；字段存在不证明已经真实执行')
    candidates = record.get('opening_candidates')
    keys = ('id', 'mechanism', 'hook', 'next_line', 'first_shot', 'reason')
    if not isinstance(candidates, list) or len(candidates) < 2 or not all(
            isinstance(c, dict) and all(text(c.get(k)) for k in keys) for c in candidates):
        return fail('OPENING_CANDIDATES', '缺少可比较的开头、接入句和已有首画面')
    if len({c['id'] for c in candidates}) != len(candidates) or len({c['mechanism'] for c in candidates}) < 2 or len({compact(c['hook']) for c in candidates}) != len(candidates):
        return fail('OPENING_CANDIDATES', '候选编号、机制或开头重复')
    selected = next((c for c in candidates if c['id'] == record.get('opening_choice')), None)
    if selected is None:
        return fail('OPENING_CHOICE', '缺少有效选择；等待用户或使用已有代选授权')
    assembled = record.get('assembled')
    if not isinstance(assembled, dict) or not text(assembled.get('script')):
        return fail('ASSEMBLED', '缺少装入所选开头的完整稿')
    script = assembled['script']
    if not compact(script).startswith(compact(selected['hook'] + selected['next_line'])):
        return fail('ASSEMBLED', '所选开头和承接句尚未进入完整稿')
    review = record.get('reader_review')
    if not isinstance(review, dict) or not all(text(review.get(k)) for k in ('takeaway', 'note', 'script_sha256')) or review.get('decision') not in ('pass', 'revise'):
        return fail('READER_REVIEW', '缺少对实际全文的整篇审读记录')
    if review['script_sha256'] != script_hash(script):
        return fail('READER_REVIEW', '审读对应旧稿；对当前全文审读并更新摘要')
    if review['decision'] == 'revise':
        return fail('BODY_DRAFT', '整篇审读发现待修问题，返回实际创作')
    return {'ready': True, 'return_to': None, 'scope': 'artifact_integrity_only',
            'writing_quality_verified': False, 'db_execution_verified': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('record', type=Path)
    args = parser.parse_args()
    try:
        result = check(json.loads(args.record.read_text(encoding='utf-8')))
    except (OSError, ValueError) as exc:
        result = {'ready': False, 'return_to': 'RECORD', 'reason': str(exc),
                  'scope': 'artifact_integrity_only', 'writing_quality_verified': False}
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result['ready'] else 2


if __name__ == '__main__':
    raise SystemExit(main())
