#!/usr/bin/env python3
"""DCVlog E0.2: offline corpus discovery and append-only additions. Stdlib only."""
import argparse, datetime, hashlib, json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / 'references' / 'corpus'
NEW = ROOT / 'batch-002-new'

def digest(data): return hashlib.sha256(data).hexdigest()

def scan(root=ROOT):
    rows=[]
    for batch,pattern in [('001','batch-001-baseline/cases.md'),('003','batch-003-raw-20261016/cases.md')]:
        p=root/pattern
        if p.is_file():
            raw=p.read_bytes()
            rows.append({'id':'B'+batch+'-COLLECTION','source_path':p.relative_to(root).as_posix(),'status':'locked','raw_hash':digest(raw),'client_count':None,'video_structure':'mixed','opening_type':None,'ending_type':None,'style_tags':[]})
    new=root/'batch-002-new'
    for p in sorted(new.glob('B002-*.md')):
        if not re.fullmatch(r'B002-\d{3,6}\.md',p.name): continue
        raw=p.read_bytes(); txt=raw.decode('utf-8')
        m=re.search(r'(?m)^client_count:\s*(\d+)\s*$',txt)
        count=int(m.group(1)) if m else None
        sidecar=p.with_suffix('.meta.json')
        meta=json.loads(sidecar.read_text(encoding='utf-8')) if sidecar.is_file() else {}
        if count is None: count=meta.get('client_count')
        tags=re.search(r'(?m)^style_tags:\s*(.*)$',txt)
        rows.append({'id':p.stem,'source_path':p.relative_to(root).as_posix(),'status':'new','raw_hash':digest(raw),'client_count':count,'video_structure':'standard_makeup_vlog','opening_type':None,'ending_type':None,'style_tags':[x.strip() for x in tags.group(1).split(',') if x.strip()] if tags else meta.get('style_tags',[])})
    return rows

def build(root=ROOT):
    rows=scan(root)
    dest=root/'catalog.json'
    tmp=dest.with_suffix('.json.tmp')
    tmp.write_text(json.dumps({'schema_version':1,'cases':rows},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    tmp.replace(dest)
    return rows

def add(source,root=ROOT,client_count=None,tags=''):
    raw=Path(source).read_bytes()
    if not raw.strip(): raise ValueError('empty case')
    rows=scan(root)
    if any(row['raw_hash']==digest(raw) for row in rows): raise ValueError('duplicate source bytes')
    new=root/'batch-002-new';new.mkdir(parents=True,exist_ok=True)
    ids=[int(p.stem.split('-')[1]) for p in new.glob('B002-*.md') if re.fullmatch(r'B002-\d{3,6}',p.stem)]
    number=max(ids,default=0)+1
    path=new/f'B002-{number:03d}.md'
    # Original bytes retained as an independent file; metadata in separate sidecar.
    with path.open('xb') as f:f.write(raw)
    if client_count is not None or tags:
        sidecar=path.with_suffix('.meta.json')
        sidecar.write_text(json.dumps({'client_count':client_count,'style_tags':[x.strip() for x in tags.split(',') if x.strip()]},ensure_ascii=False,indent=2),encoding='utf-8')
    build(root)
    return path

def main():
    parser=argparse.ArgumentParser();sub=parser.add_subparsers(dest='cmd',required=True)
    sub.add_parser('list');sub.add_parser('build');a=sub.add_parser('add');a.add_argument('file');a.add_argument('--client-count',type=int);a.add_argument('--tags',default='')
    args=parser.parse_args()
    if args.cmd=='add': print(add(args.file,client_count=args.client_count,tags=args.tags))
    else:
        rows=build() if args.cmd=='build' else scan()
        print(json.dumps(rows,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
