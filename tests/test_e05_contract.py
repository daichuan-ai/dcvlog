from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[1]
class TestE05(unittest.TestCase):
 def test_mirrors(self):
  for rel in ['SKILL.md','references/opening-ending.md','references/interview-engine.md','references/visual-observation-e05.md','references/creative-engine-e02.md','references/assembly-check-e03.md']:
   self.assertEqual((ROOT/rel).read_bytes(),(ROOT/'skills/dcvlog'/rel).read_bytes(),rel)
 def test_rules(self):
  op=(ROOT/'references/opening-ending.md').read_text()
  self.assertIn('禁止再问“纯画面还是配旁白”',op)
  self.assertIn('约3—4秒',op)
  v=(ROOT/'references/visual-observation-e05.md').read_text()
  self.assertIn('不发，直接写文案',v)
  self.assertIn('不得假装看过',v)
  it=(ROOT/'references/interview-engine.md').read_text()
  self.assertIn('仅限非新娘跟妆',it)
if __name__=='__main__': unittest.main()
