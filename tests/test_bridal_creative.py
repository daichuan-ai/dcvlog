"""Check recoverable handoff/version errors without prescribing narration style."""
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('creative_gate', ROOT / 'skills/dcvlog/tools/check_bridal_creative.py')
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


def record():
    script = '好看也得舒服。今天她换了双鞋。鞋子合脚，她就穿着走了。'
    return {
        'schema_version': 2,
        'rough_draft': '她换了鞋，穿着走了。',
        'story_brief': {'event': '换鞋', 'author_point': '在意舒服', 'audience': '在好看与舒服间选择的人'},
        'body_draft': script,
        'db_execution': {'source': 'fixture', 'modules': ['creator', 'flow']},
        'opening_candidates': [
            {'id': '1', 'mechanism': '观点', 'hook': '好看也得舒服。', 'next_line': '今天她换了双鞋。', 'first_shot': '鞋', 'reason': '观点'},
            {'id': '2', 'mechanism': '事实前置', 'hook': '她把鞋换了。', 'next_line': '这是今天的小事。', 'first_shot': '鞋', 'reason': '事情'}],
        'opening_choice': '1',
        'assembled': {'script': script},
        'reader_review': {'takeaway': '在意人的舒服', 'decision': 'pass', 'note': '审读示例，测试不判断文笔', 'script_sha256': gate.script_hash(script)}
    }


class CreativeGateTests(unittest.TestCase):
    def test_natural_action_ending_needs_no_emotion_quota(self):
        result = gate.check(record())
        self.assertTrue(result['ready'])
        self.assertFalse(result['writing_quality_verified'])
        self.assertFalse(result['db_execution_verified'])

    def test_legacy_record_returns_to_brief_not_interview(self):
        r = record(); del r['story_brief']; r['emotion_plan'] = {'center_judgment': '旧计划'}
        self.assertEqual(gate.check(r)['return_to'], 'STORY_BRIEF')

    def test_missing_source_does_not_claim_db_success(self):
        r = record(); del r['db_execution']
        self.assertEqual(gate.check(r)['return_to'], 'DB_EXECUTION')

    def test_missing_actual_body_cannot_pass(self):
        r = record(); r['body_draft'] = ''
        self.assertEqual(gate.check(r)['return_to'], 'BODY_DRAFT')

    def test_duplicate_candidates_need_recovery(self):
        for key in ('id', 'hook', 'mechanism'):
            r = record(); r['opening_candidates'][1][key] = r['opening_candidates'][0][key]
            self.assertEqual(gate.check(r)['return_to'], 'OPENING_CANDIDATES')

    def test_choice_must_match_actual_candidate(self):
        for choice in (None, '3'):
            r = record(); r['opening_choice'] = choice
            self.assertEqual(gate.check(r)['return_to'], 'OPENING_CHOICE')

    def test_unassembled_hook_is_detected(self):
        r = record(); r['opening_choice'] = '2'
        self.assertEqual(gate.check(r)['return_to'], 'ASSEMBLED')

    def test_missing_or_stale_review_needs_current_read(self):
        r = record(); del r['reader_review']
        self.assertEqual(gate.check(r)['return_to'], 'READER_REVIEW')
        r = record(); r['assembled']['script'] += '又改了一句。'
        self.assertEqual(gate.check(r)['return_to'], 'READER_REVIEW')

    def test_known_quality_failure_returns_to_creation(self):
        r = record(); r['reader_review']['decision'] = 'revise'
        self.assertEqual(gate.check(r)['return_to'], 'BODY_DRAFT')

    def test_records_never_prove_semantic_quality(self):
        r = record(); r['reader_review']['takeaway'] = '这个结论也可能判断错'
        self.assertFalse(gate.check(r)['writing_quality_verified'])


if __name__ == '__main__':
    unittest.main()
