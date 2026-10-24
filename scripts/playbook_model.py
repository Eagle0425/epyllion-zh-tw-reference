"""Reading/printing composition uses references, never a second translation store."""
from quality_model import load

CORE=['academic','crafter','daredevil','nature-adept','seer','warrior']
EXTRA=['elementalist','envoy','orphan','rebel']
NAMES=['學者','工匠','勇者','自然之民','先知','戰士','元素使','使節','孤龍','反叛者']
def ref(eid,field,index):return {'entry_id':eid,'field':field,'index':index}
def compose(entries):
    by={e['id']:e for e in entries}
    def refs(eid,field='paragraphs',indexes=None):
        return [ref(eid,field,i) for i in (range(len(by[eid].get(field,[]))) if indexes is None else indexes)]
    def section(sid,title,blocks,**extra):return dict(id=sid,title=title,blocks=blocks,**extra)
    books=[]
    for n,role in enumerate(CORE+EXTRA):
        core=role in CORE;eid=('pb-' if core else 'ed-')+role;e=by[eid]
        b={'id':role,'entry_id':eid,'title':NAMES[n],'en':e['en'],'edition':'core' if core else 'expansion','image':e.get('image'),'pdf_id':'zh-playbooks' if core else 'zh-ed-playbooks','pdf_page':(n if core else n-6)*2+1}
        if core:
            sections=[section('identity','認識這隻龍',refs(eid,indexes=[0])),section('creation','屬性、美德與家族義務',refs(eid,indexes=[1,2])),section('appearance','名字、色彩與外觀',refs(eid,indexes=[4])+refs(eid,'bullets')),section('fellowship','夥伴關係與友誼寶石',refs(eid,indexes=[5])),section('growth','成長與月亮',refs(eid,indexes=[7,8])+refs('core-xp-track-lengths','bullets'))]
            signature={'academic':'expertise','crafter':'dragon-trade','daredevil':'beast-companion','nature-adept':'wild-speech','seer':'haunting-visions','warrior':'scales-honor'}[role]
            moves=sorted([x for x in entries if x.get('role')==role and x['category']=='playbook-moves'],key=lambda x:x['id']!=f'pb-{role}-{signature}')
            sections.append(section('starting','選擇你的動作',refs(eid,indexes=[3])))
            for i,m in enumerate(moves):
                ps=refs(m['id']);bs=refs(m['id'],'bullets')
                if role=='academic' and i==0:blocks=ps[:1]+bs+ps[1:]
                elif role=='crafter' and i==0:blocks=ps[:3]+bs+ps[3:]
                elif m['id'] in ['pb-daredevil-clear-headed','pb-warrior-battle-plan']:blocks=ps[:1]+bs+ps[1:]
                elif m['id']=='pb-seer-touch-darkness':blocks=ps[:1]+bs[:3]+ps[1:]+bs[3:]
                else:blocks=ps+bs
                sections.append(section(m['id'],m['title'],blocks,en=m['en'],move=True,signature=i==0,entry_id=m['id']))
            sections.append(section('shadows','暗影軌與暗影化身',refs(eid,indexes=[9,10,6])))
        else:
            sections=[section('identity','認識這隻龍',refs(eid,indexes=[0])),section('creation','屬性、美德與家族義務',refs(eid,indexes=[2])),section('appearance','名字、色彩與外觀',refs(eid,indexes=[1])),section('fellowship','夥伴關係與友誼寶石',refs(eid,indexes=[3]))]
            growth=refs('ed-playbook-growth',indexes=[0,1,2])
            if role in ['orphan','rebel']:growth+=refs(eid,indexes=[len(e['paragraphs'])-1])
            sections.append(section('growth','成長與月亮',growth))
            sections.append(section('starting','選擇你的動作',refs(eid,indexes=[4])))
            mapping={'elementalist':[(5,6,7),(8,),(9,),(10,),(11,)],'envoy':[(5,6),(7,),(8,),(9,),(10,)],'orphan':[(5,6,7),(8,),(9,),(10,),(11,)],'rebel':[(5,6),(7,),(8,),(9,),(10,)]}
            for i,indexes in enumerate(mapping[role]):
                title=e['paragraphs'][indexes[0]].split('（')[0]
                sections.append(section(f'{eid}-move-{i+1}',title,refs(eid,indexes=indexes),move=True,signature=i==0))
            shadow_index={'elementalist':12,'envoy':11,'orphan':12,'rebel':11}[role]
            sections.append(section('shadows','暗影軌與暗影化身',refs('ed-playbook-growth',indexes=[3,4])+refs(eid,indexes=[shadow_index])))
        b['sections']=sections;books.append(b)
    return books

def resolve(books,entries):
    by={e['id']:e for e in entries}
    return [dict(b,sections=[dict(s,blocks=[dict(r,text=by[r['entry_id']][r['field']][r['index']]) for r in s['blocks']]) for s in b['sections']]) for b in books]

def validate_composition(books,entries):
    by={e['id']:e for e in entries};covered=set()
    assert len(books)==10 and len({b['id'] for b in books})==10
    for b in books:
        assert sum(s.get('move',False) for s in b['sections'])==5,b['id']
        assert sum(s.get('signature',False) for s in b['sections'])==1,b['id']
        for s in b['sections']:
            for r in s['blocks']:
                assert r['entry_id'] in by
                assert by[r['entry_id']][r['field']][r['index']]
                covered.add((r['entry_id'],r['field'],r['index']))
    required={(e['id'],f,i) for e in entries if e['id'] in {b['entry_id'] for b in books}|{'ed-playbook-growth'} or e['category']=='playbook-moves' for f in ['paragraphs','bullets'] for i in range(len(e.get(f,[])))}
    assert required<=covered,sorted(required-covered)
    return {'playbooks':len(books),'moves':50,'canonical_blocks':len(required),'uncovered_blocks':0}

if __name__=='__main__':
    _,entries,_=load();print(validate_composition(compose(entries),entries))
