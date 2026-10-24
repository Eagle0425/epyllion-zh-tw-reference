"""Merge editable translation records and prepare a buildless portable website."""
import json, pathlib, collections, shutil, re
ROOT=pathlib.Path(__file__).resolve().parents[1]
DIST=ROOT/'dist'
entries=[]
files=sorted((ROOT/'content').glob('*.json'))
# A combined GM file replaces intermediate chapter files.
if (ROOT/'content/gm.json').exists(): files=[p for p in files if not re.fullmatch(r'gm-\d+\.json',p.name)]
replacements={'磐石之月':'堅石之月','虛空之月':'虛無之月','招牌動作':'特色動作','招式':'動作','紅寶石家族':'紅玉家族','角色劇本':'扮演書','危機':'危害','奧術之耳':'秘法音感','龍族工藝':'巨龍手藝','細節之眼':'洞察之眼','眾月紀念碑':'月之聖碑','巧爪':'鬼爪神工','野獸夥伴':'動物夥伴','分擔重擔':'承擔黑暗','野性言語':'荒野語言','黑暗縈繞的幻視':'黑暗幻象','戰鬥計畫':'戰鬥計策','親合龍群':'親密龍群','年齡：長老':'年齡：上古巨龍','八郎':'哈奇洛','冒險家':'勇者'}
def clean(v):
    if isinstance(v,str):
        for a,b in replacements.items(): v=v.replace(a,b)
        return v
    if isinstance(v,list): return [clean(x) for x in v]
    if isinstance(v,dict): return {k:clean(x) for k,x in v.items()}
    return v
for path in files:
    records=json.loads(path.read_text(encoding='utf-8-sig'))
    assert isinstance(records,list),path
    entries.extend(clean(records))
source_order={'core':0,'playbooks':1,'encyclopedia':2,'ed-playbooks':3}
entries.sort(key=lambda e:(source_order.get(e['source']['file'],9),int(re.search(r'\d+',str(e['source']['pages'])).group()),e['id']))
ids=[x['id'] for x in entries]
assert len(ids)==len(set(ids)), f'Duplicate IDs: {[k for k,v in collections.Counter(ids).items() if v>1]}'
for e in entries:
    for k in ['id','title','en','category','kind','source','paragraphs']: assert k in e,(e.get('id'),k)
    assert e['paragraphs'] or e.get('bullets'),e['id']
    assert e['source'].get('pages') and e['source'].get('book'),e['id']
    assert '\ufffd' not in json.dumps(e,ensure_ascii=False),f'Broken encoding: {e["id"]}'
roles={
 'academic':{'title':'學者','image':'academic_ft3'},'crafter':{'title':'工匠','image':'crafter_f3'},
 'daredevil':{'title':'勇者','image':'dare_devil_ft3'},'nature-adept':{'title':'自然之民','image':'nature_adept_ft3'},
 'seer':{'title':'先知','image':'seer_ft3'},'warrior':{'title':'戰士','image':'warier_ft3_rescan_(1)'}}
for e in entries:
    if e['category']=='playbooks' and e.get('role') in roles:e['image']='assets/'+roles[e['role']]['image']+'.webp'
    if e['category']=='expansion-playbooks' and e['id'].endswith('-dm'):e['category']='gm'
sources={
 'zh-moves':{'title':'中文基本動作表','path':'downloads/epyllion-moves-zh.pdf','input':'翻譯/Epyllion_Moves_zhTW.pdf','description':'既有翻譯，一頁。研讀他龍題數尚未同步網頁校訂。','language':'zh','offset':0},
 'zh-playbooks':{'title':'中文核心角色卡','path':'downloads/epyllion-playbooks-zh.pdf','input':'翻譯/Epyllion_Playbooks_zhTW.pdf','description':'既有翻譯，六種角色、共十二頁。原始列印版。','language':'zh','offset':0},
 'core':{'title':'Epyllion 核心規則書','path':'downloads/epyllion-core-en.pdf','input':'原文/Epyllion_20160714.pdf','description':'英文原書，2016 版。印刷頁碼比 PDF 頁序多一頁。','language':'en','offset':-1},
 'playbooks':{'title':'英文核心扮演書','path':'downloads/epyllion-playbooks-en.pdf','input':'原文/Playbooks_20160714.pdf','description':'六種獨立角色表，作為網站規則校訂依據。','language':'en','offset':0},
 'moves':{'title':'英文基本動作表','path':'downloads/epyllion-moves-en.pdf','input':'原文/Moves_20160714.pdf','description':'一頁基本動作原文，供數值與觸發條件核對。','language':'en','offset':0},
 'dm':{'title':'英文龍主工作表','path':'downloads/epyllion-dm-en.pdf','input':'原文/DM_Sheet_20160715.pdf','description':'目標、原則、龍主動作、NPC 靈感與危害紀錄。','language':'en','offset':0},
 'map':{'title':'龍域空白地圖','path':'downloads/epyllion-map.pdf','input':'原文/Map_20190722.pdf','description':'2019 版空白地圖，適合列印後共同繪製。','language':'en','offset':0},
 'encyclopedia':{'title':'Encyclopedia Draconica','path':'downloads/encyclopedia-draconica-en.pdf','input':'原文/460322546-EncyclopediaDraconica-20180222-pdf.pdf','description':'十七篇傳說、四種擴充扮演書與特殊動作。','language':'en','offset':1},
 'ed-playbooks':{'title':'英文擴充扮演書','path':'downloads/epyllion-ed-playbooks-en.pdf','input':'原文/460322549-Epyllion-EDPlaybooks-20180219.pdf','description':'元素使、使節、孤龍、反叛者，八頁角色表。','language':'en','offset':0}}
for s in sources.values():
    target=DIST/s['path'];target.parent.mkdir(parents=True,exist_ok=True)
    original=ROOT.parent/s.pop('input')
    if original.exists():shutil.copyfile(original,target)
    else:assert target.exists(),f'Missing source PDF and retained download: {target.name}'
for e in entries:assert e['source']['file'] in sources,(e['id'],e['source'])
glossary=[['龍域','Dragonia','dragonia-land'],['龍群','Clutch','clutch'],['龍主','Dragonmaster / DM','gm-agendas'],['魅力','Charm','dice'],['勇氣','Courage','dice'],['機巧','Cunning','dice'],['友誼寶石','Friendship Gems','gems'],['暗影','Shadow','shadows'],['暗影化身','Shadowself','shadowself'],['若鱗幼龍','Raw-Scaled Drake',''],['青年飛龍','Winged Drake',''],['成年牙龍','Long-Toothed Dragon',''],['壯年鬚龍','Bearded Dragon',''],['上古巨龍','Elder Dragon',''],['遠古巨龍','Ancient',''],['神話巨龍','Mystic',''],['敏鐸司／橡木家族','Myndoth / House of Oak',''],['雪思可／翡翠家族','Semscale / House of Jade',''],['科布羅斯／紅玉家族','Kebros / House of Ruby',''],['洛斯加／黃金家族','Rothscar / House of Gold',''],['布蘭巴克／鋼鐵家族','Brynback / House of Steel',''],['塔希絲／鑽石家族','Tessith / House of Diamond',''],['虛無之月','Void Moon','moon-magic'],['自由之月','Liberty Moon','moon-magic'],['堅石之月','Stone Moon','moon-magic'],['靈魂之月','Spirit Moon','moon-magic'],['風暴之月','Storm Moon','moon-magic']]
for row in glossary:
    if not row[2]:
        candidates=[e for e in entries if row[1].split(' / ')[0].lower() in e['en'].lower()]
        if candidates:row[2]=candidates[0]['id']
for e in entries:
    if e['category'] in ['playbooks','moves','playbook-moves']:glossary.append([e['title'],e['en'],e['id']])
stats={'total':len(entries),'categories':dict(collections.Counter(e['category'] for e in entries)),'chars':sum(len(''.join(e['paragraphs'])+''.join(e.get('bullets',[]))) for e in entries),'files':[p.name for p in files]}
data={'entries':entries,'sources':sources,'roles':roles,'glossary':glossary,'stats':stats}
(DIST/'data.js').write_text('window.EPYLLION = '+json.dumps(data,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf-8')
index=(DIST/'index.html').read_text(encoding='utf-8')
(DIST/'gm.html').write_text(index.replace('<title>龍族史詩 Epyllion｜繁體中文手冊</title>','<title>龍主工作台｜龍族史詩 Epyllion</title>'),encoding='utf-8')
(DIST/'.nojekyll').write_text('',encoding='utf-8')
print(json.dumps(stats,ensure_ascii=False,indent=2))
