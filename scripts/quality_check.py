"""Separate schema, source, drift and review-evidence checks from semantics."""
import argparse,hashlib,json,pathlib,re,sys
from quality_model import ROOT,read,digest,load,data_js
if (ROOT/'.quality-deps').exists():sys.path.insert(0,str(ROOT/'.quality-deps'))
from jsonschema import Draft202012Validator
def check(root=ROOT,require_semantic=False):
    errors=[];warnings=[];project,entries,sources=load(root)
    def error(message):errors.append(message)
    def validate(schema_name,value,label):
        for issue in Draft202012Validator(read(root/'translation/schemas'/schema_name)).iter_errors(value):error(f'{label}: {list(issue.absolute_path)} {issue.message}')
    validate('project.schema.json',project,'project');validate('sources.schema.json',sources,'sources')
    for name in project['content_files']:validate('entries.schema.json',read(root/'content'/name),name)
    glossary=read(root/'translation/glossary.json');validate('glossary.schema.json',glossary,'glossary')
    ids=[e['id'] for e in entries];idset=set(ids)
    if len(idset)!=len(ids):error('Duplicate entry IDs.')
    if len(entries)!=project['expected_entries']:error('Entry count differs from manifest; review additions/removals.')
    if {p.name for p in (root/'content').glob('*.json')}!=set(project['content_files']):error('Unlisted or missing content files.')
    for sid,book in sources.items():
        path=root/'dist'/book['path']
        if not path.is_file():error(f'{sid}: missing source PDF');continue
        if hashlib.sha256(path.read_bytes()).hexdigest()!=book['sha256']:error(f'{sid}: PDF changed; review source edition and provenance.')
    artifacts=read(root/'translation/artifacts.json')['artifacts']
    if {a['path'] for a in artifacts}!={str(p.relative_to(root/'dist')).replace('\\','/') for p in (root/'dist/downloads').glob('*.pdf')}:error('PDF artifact inventory differs from downloads.')
    for artifact in artifacts:
        path=root/'dist'/artifact['path']
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest()!=artifact['sha256']:error(f'{artifact["path"]}: artifact changed; update its review record.')
    provenance=read(root/'translation/provenance.json')['entries'];reviews=read(root/'translation/reviews.json')['entries'];alignment=read(root/'translation/alignment.json')['entries']
    for label,records in [('provenance',provenance),('reviews',reviews),('alignment',alignment)]:
        if set(records)!=idset:error(f'{label}: IDs differ from canonical entries.')
    pending=0;linked=0;total_blocks=0;block_ids=set()
    for e in entries:
        eid=e['id'];sid=e['source']['file']
        if sid not in sources:error(f'{eid}: unknown source');continue
        if eid not in provenance or eid not in reviews or eid not in alignment:continue
        book=sources[sid];p=provenance[eid];r=reviews[eid];blocks=alignment[eid]
        if p['book_id']!=sid or p['label']!=e['source']['pages']:error(f'{eid}: stale source locator.')
        if p['source_sha256']!=book['sha256'] or r['source_sha256']!=book['sha256']:error(f'{eid}: stale source fingerprint.')
        offset=0 if p['page_kind']=='pdf' else book['offset']
        expected=[{'start':x['start']+offset,'end':x['end']+offset} for x in p['ranges']]
        if expected!=p['pdf_ranges']:error(f'{eid}: incorrect printed/PDF page conversion.')
        for span in p['pdf_ranges']:
            if not 1<=span['start']<=span['end']<=book['pdf_pages']:error(f'{eid}: page outside PDF bounds.')
        if r['content_sha256']!=digest(e):error(f'{eid}: translation changed; review record is stale.')
        expected_blocks=[(field,i,text) for field in ['paragraphs','bullets'] for i,text in enumerate(e.get(field,[]))]
        if len(blocks)!=len(expected_blocks):error(f'{eid}: target block count changed; update alignment explicitly.')
        for block,(field,i,text) in zip(blocks,expected_blocks):
            total_blocks+=1
            if not block['id'].startswith(eid+':') or block['id'] in block_ids:error(f'{eid}: invalid or duplicate target block ID.')
            block_ids.add(block['id'])
            if block['field']!=field or block['index']!=i or block['target_sha256']!=digest(text):error(f'{eid}: stale/reordered target block {block["id"]}.')
            if block['source_blocks']:linked+=1
            for ref in block['source_blocks']:
                source=sources.get(ref.get('book_id'))
                if not source or ref.get('source_sha256')!=source['sha256'] or not 1<=ref.get('pdf_page',0)<=source['pdf_pages'] or not ref.get('block_id') or not ref.get('locator') or not re.fullmatch('[0-9a-f]{64}',ref.get('text_sha256','')):error(f'{eid}: invalid source-block evidence for {block["id"]}.')
        if r['semantic_status'] not in ['pending','verified','needs-revision']:error(f'{eid}: invalid review status.')
        if r['semantic_status']=='verified':
            if not r.get('reviewer') or not r.get('evidence') or any(not b['source_blocks'] for b in blocks):error(f'{eid}: verified review lacks reviewer/evidence/source-block alignment.')
        else:pending+=1
        if '\ufffd' in json.dumps(e,ensure_ascii=False):error(f'{eid}: broken encoding.')
    term_ids=set()
    for term in glossary['terms']:
        if term['id'] in term_ids:error('Duplicate terminology IDs.')
        term_ids.add(term['id'])
        if term['entry_id'] is not None and term['entry_id'] not in idset:error(f'{term["id"]}: glossary link has no entry.')
        for e in entries:
            text=' '.join([e['title'],*e['paragraphs'],*e.get('bullets',[])])
            for forbidden in term['forbidden']:
                if forbidden in text:error(f'{e["id"]}: prohibited term {forbidden!r}; expected {term["zh"]!r}.')
    structural_errors=list(errors)
    if require_semantic and pending:error(f'{pending} entries lack evidence-backed semantic review.')
    if pending:warnings.append(f'{pending} existing entries await formal semantic review; structural success is not proof of complete translation.')
    if linked<total_blocks:warnings.append(f'{total_blocks-linked}/{total_blocks} target blocks lack source-block alignment.')
    if (root/'dist/data.js').read_text(encoding='utf-8')!=data_js(root):
        error('data.js differs from canonical content; run sync-data.py.');structural_errors.append(errors[-1])
    return {'schema_version':1,'structural_pass':not structural_errors,'semantic_pass':not errors and pending==0 and linked==total_blocks,'gate_pass':not errors,'entries':len(entries),'semantic_pending':pending,'aligned_target_blocks':linked,'target_blocks':total_blocks,'errors':errors,'warnings':warnings}
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--require-semantic',action='store_true');parser.add_argument('--report',type=pathlib.Path);args=parser.parse_args();result=check(require_semantic=args.require_semantic)
    if args.report:args.report.parent.mkdir(parents=True,exist_ok=True);args.report.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False,indent=2));raise SystemExit(0 if result['gate_pass'] else 1)
