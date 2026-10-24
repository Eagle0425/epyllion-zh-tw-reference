"""Register inspected PDFs and bind downloadable copies to their build record."""
import argparse,hashlib,json,pathlib,shutil
from quality_model import ROOT,read,digest,load
from playbook_model import compose
parser=argparse.ArgumentParser();parser.add_argument('--pdf-directory',type=pathlib.Path,required=True);args=parser.parse_args()
_,entries,_=load();build=read(ROOT/'translation/playbook-pdf-build.json')
assert build['canonical_content_sha256']==digest(entries) and build['composition_sha256']==digest(compose(entries))
sources=read(ROOT/'translation/sources.json');artifacts=read(ROOT/'translation/artifacts.json')
for sid,name,title,pages,description in [('zh-playbooks','epyllion-playbooks-zh.pdf','中文核心角色卡（校訂版）',12,'六種核心扮演書，各兩頁；完整創角選項、動作、成長與暗影，依網站同一份校訂資料產生。'),('zh-ed-playbooks','epyllion-ed-playbooks-zh.pdf','中文擴充角色卡（校訂版）',8,'元素使、使節、孤龍、反叛者，各兩頁；含完整動作、選項與各自成長差異。')]:
    source=args.pdf_directory/name;sha=hashlib.sha256(source.read_bytes()).hexdigest()
    assert sha==next(x['sha256'] for x in build['outputs'] if x['name']==name)
    path='downloads/'+name;shutil.copyfile(source,ROOT/'dist'/path)
    sources[sid]={'id':sid,'title':title,'path':path,'description':description,'language':'zh','offset':0,'sha256':sha,'pdf_pages':pages}
    record={'path':path,'sha256':sha,'role':'generated-translation','review_status':'source-compared','notes':'2026-10-24：從標準正文重製；逐區塊文字驗證及全頁渲染檢查，獨立語義複核仍待完成。'}
    existing=next((a for a in artifacts['artifacts'] if a['path']==path),None)
    if existing:existing.update(record)
    else:artifacts['artifacts'].append(record)
artifacts['known_differences']=[d for d in artifacts['known_differences'] if d['artifact']!='downloads/epyllion-playbooks-zh.pdf']
for name,value in [('sources',sources),('artifacts',artifacts)]:
    (ROOT/f'translation/{name}.json').write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('Registered source-comparison records for 20 generated PDF pages.')
