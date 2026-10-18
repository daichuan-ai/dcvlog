from pathlib import Path
import unittest
R=Path(__file__).resolve().parents[1]
class TestE06(unittest.TestCase):
 def test_mirror(self):
  for p in [R/'SKILL.md',R/'VERSION',* (R/'references').rglob('*')]:
   if p.is_file(): self.assertEqual(p.read_bytes(),(R/'skills/dcvlog'/p.relative_to(R)).read_bytes())
 def test_contract(self):
  s=(R/'references/e06-writing-refinement.md').read_text()
  for key in ['强画面','强情绪','强数字','纯文案','只发第1位','只发第2位','人物印象','自然结束','不再追问','完整连续旁白']:
   self.assertIn(key,s)
 def test_version(self):
  self.assertEqual((R/'VERSION').read_text().strip(),'1.9.2')
  self.assertIn('version: "1.9.2"',(R/'SKILL.md').read_text())
if __name__=="__main__": unittest.main()
