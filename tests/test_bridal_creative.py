"""Exercise missing-stage recovery and actual text assembly, not prose quality."""
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('creative_gate', ROOT / 'skills/dcvlog/tools/check_bridal_creative.py')
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


def record():
    return {
        'rough_draft': '她问了时间。后来坐下喝水。',
        'emotion_plan': {'center_judgment': '原来忙碌也有温度', 'audience': '忙于安排事情的人',
                         'progression': [{'fact': '问时间', 'response': '真是一刻也闲不下来',
                                          'serves_center': '先看到忙碌'}],
                         'ending_response': '原来忙碌也有温度。'},
        'body_draft': '她问了时间。真是一刻也闲不下来。后来坐下喝水。原来忙碌也有温度。',
        'opening_brief': {'core_judgment': '忙碌也有温度', 'audience': '忙于安排事情的人',
                          'tension': '忙与照顾并存', 'fact_anchors': ['问时间', '坐下喝水'],
                          'viewer_question': '忙碌中被照顾是什么感觉'},
        'opening_candidates': [
            {'id': '1', 'mechanism': '概念反差', 'hook': '忙碌也有温度。',
             'next_line': '她问了时间。', 'first_shot': '问时间的已有画面', 'reason': '建立判断'},
            {'id': '2', 'mechanism': '结果前置', 'hook': '她终于坐下喝水了。',
             'next_line': '前面一直在问时间。', 'first_shot': '杯子', 'reason': '想看前因'}],
        'opening_choice': '1',
        'assembled': {'script': '忙碌也有温度。\n她问了时间。真是一刻也闲不下来。\n后来坐下喝水。原来忙碌也有温度。',
                      'emotion_evidence': ['真是一刻也闲不下来。'],
                      'ending_response': '原来忙碌也有温度。', 'promise_evidence': '后来坐下喝水。'}
    }


class CreativeGateTests(unittest.TestCase):
    def test_complete_artifacts_do_not_claim_writing_quality(self):
        result = gate.check(record())
        self.assertTrue(result['ready'])
        self.assertFalse(result['writing_quality_verified'])

    def test_missing_emotion_returns_to_emotion_plan(self):
        r = record(); del r['emotion_plan']['progression']
        self.assertEqual(gate.check(r)['return_to'], 'EMOTION_PLAN')

    def test_missing_brief_cannot_jump_to_candidates(self):
        r = record(); del r['opening_brief']
        self.assertEqual(gate.check(r)['return_to'], 'OPENING_BRIEF')

    def test_duplicate_mechanisms_are_not_different_choices(self):
        r = record(); r['opening_candidates'][1]['mechanism'] = r['opening_candidates'][0]['mechanism']
        self.assertEqual(gate.check(r)['return_to'], 'OPENING_CANDIDATES')

    def test_unselected_or_unknown_choice_waits(self):
        for choice in (None, '3'):
            r = record(); r['opening_choice'] = choice
            self.assertEqual(gate.check(r)['return_to'], 'OPENING_CHOICE')

    def test_selected_hook_and_bridge_must_be_in_actual_script(self):
        r = record(); r['opening_choice'] = '2'
        self.assertEqual(gate.check(r)['return_to'], 'ASSEMBLED')

    def test_declared_emotion_evidence_must_exist_in_text(self):
        r = record(); r['assembled']['emotion_evidence'] = ['正文里没有这句话']
        self.assertEqual(gate.check(r)['return_to'], 'BODY_DRAFT')

    def test_ending_and_promise_cannot_be_checked_with_empty_flags(self):
        r = record(); r['assembled']['ending_response'] = True
        self.assertEqual(gate.check(r)['return_to'], 'EMOTION_PLAN')
        r = record(); r['assembled']['promise_evidence'] = '未写入的兑现'
        self.assertEqual(gate.check(r)['return_to'], 'ASSEMBLED')


if __name__ == '__main__':
    unittest.main()
