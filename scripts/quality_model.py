"""Canonical data access; no rewriting or approval inference."""
import collections,hashlib,json,pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
def read(path):return json.loads(path.read_text(encoding='utf-8-sig'))
def digest(value):return hashlib.sha256(json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def load(root=ROOT):
    project=read(root/'translation/project.json')
    entries=[entry for name in project['content_files'] for entry in read(root/'content'/name)]
    sources=read(root/'translation/sources.json');provenance=read(root/'translation/provenance.json')['entries']
    order={'core':0,'playbooks':1,'encyclopedia':2,'ed-playbooks':3}
    entries.sort(key=lambda e:(order.get(e['source']['file'],9),provenance[e['id']]['pdf_ranges'][0]['start'],e['id']))
    return project,entries,sources
def public_data(root=ROOT):
    project,entries,sources=load(root);reviews=read(root/'translation/reviews.json')['entries'];provenance=read(root/'translation/provenance.json')['entries'];glossary=read(root/'translation/glossary.json')['terms']
    public_entries=[dict(e,review_status=reviews[e['id']]['semantic_status'],source_ref=provenance[e['id']]) for e in entries]
    stats={'total':len(entries),'categories':dict(collections.Counter(e['category'] for e in entries)),'chars':sum(len(''.join(e['paragraphs'])+''.join(e.get('bullets',[]))) for e in entries),'files':project['content_files']}
    states=collections.Counter(r['semantic_status'] for r in reviews.values())
    return {'entries':public_entries,'sources':sources,'roles':project['roles'],'glossary':[[t['zh'],t['en'],t['entry_id']] for t in glossary if t['status']!='deprecated'],'stats':stats,'quality':{'schema_version':1,'reviewed':states.get('verified',0),'pending':states.get('pending',0)+states.get('needs-revision',0),'scope':'Evidence-backed semantic review; page ranges alone do not establish completeness.','content_sha256':digest(entries)}}
def data_js(root=ROOT):return 'window.EPYLLION = '+json.dumps(public_data(root),ensure_ascii=False,separators=(',',':'))+';\n'
