import importlib.util, tempfile, pathlib, hashlib, json
P=pathlib.Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('case_catalog',P/'tools/case_catalog.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
with tempfile.TemporaryDirectory() as td:
 root=pathlib.Path(td); (root/'batch-002-new').mkdir();
 source=root/'sample.txt';raw='今天一位客人，做了自然妆。\n'.encode();source.write_bytes(raw)
 added=m.add(source,root,client_count=1,tags='自然,单客')
 assert added.read_bytes()==raw
 assert len(m.scan(root))==1
 assert m.scan(root)[0]['client_count']==1
 assert m.scan(root)[0]['style_tags']==['自然','单客']
 assert m.scan(root)[0]['raw_hash']==hashlib.sha256(raw).hexdigest()
 try:m.add(source,root)
 except ValueError:pass
 else:raise AssertionError('duplicate not rejected')
 second=root/'second.txt';second.write_text('另一位客人。',encoding='utf-8')
 m.add(second,root);assert len(m.scan(root))==2
 assert len(json.loads((root/'catalog.json').read_text())['cases'])==2
print('E0.2 dynamic corpus tests: PASS')
