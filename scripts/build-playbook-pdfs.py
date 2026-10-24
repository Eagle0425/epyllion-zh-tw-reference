"""Create two-page Chinese playbooks from exactly the same blocks as the website."""
import argparse,hashlib,json,pathlib,re,sys
from xml.sax.saxutils import escape
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph,Spacer,KeepTogether,Frame,Flowable
from quality_model import ROOT,load,digest,read
from playbook_model import compose,resolve,validate_composition

INK=colors.HexColor('#263b35');GOLD=colors.HexColor('#90632c');PALE=colors.HexColor('#e6ebe3')
parser=argparse.ArgumentParser();parser.add_argument('--font-directory',type=pathlib.Path,required=True);args=parser.parse_args()
for family,name in [('Body','JasonHandwriting2-Regular'),('Emphasis','JasonHandwriting2-SemiBold'),('Section','JasonHandwriting1-Medium'),('Title','JasonHandwriting1-SemiBold')]:pdfmetrics.registerFont(TTFont(family,str(args.font_directory/(name+'.ttf'))))
_,entries,sources=load();books=resolve(compose(entries),entries);validate_composition(compose(entries),entries)
OUT=ROOT.parent/'output/pdf';OUT.mkdir(parents=True,exist_ok=True)
W,H=A4;M=34;GAP=21;CW=(W-2*M-GAP)/2;TOP=H-94;BOTTOM=43;HEIGHT=TOP-BOTTOM
audit=[]
def safe(text):
    text=re.sub('[−–—‑]','-',text)
    return escape(text).replace('①','<br/>①').replace('②','<br/>②').replace('③','<br/>③')
def styles(size):
    return {'body':ParagraphStyle('body',fontName='Body',fontSize=size,leading=size*1.48,textColor=INK,wordWrap='CJK',spaceAfter=5),
    'heading':ParagraphStyle('heading',fontName='Section',fontSize=15,leading=20,textColor=INK,spaceBefore=9,spaceAfter=7),
    'move':ParagraphStyle('move',fontName='Emphasis',fontSize=13,leading=18,textColor=INK,spaceBefore=8,spaceAfter=6),
    'label':ParagraphStyle('label',fontName='Emphasis',fontSize=9,leading=13,textColor=GOLD,spaceAfter=4)}
class Tracks(Flowable):
    def __init__(self,kind):Flowable.__init__(self);self.kind=kind;self.width=CW;self.height=108 if kind=='xp' else 29
    def draw(self):
        c=self.canv;c.setStrokeColor(INK);c.setFillColor(INK);c.setFont('Emphasis',10)
        if self.kind=='xp':
            names=['若鱗幼龍','青年飛龍','成年牙龍','壯年鬚龍','上古巨龍']
            for i,(name,count,moon) in enumerate(zip(names,[5,4,4,3,3],[0,0,1,2,3])):
                y=90-i*20;c.drawString(0,y,name);c.setFont('Body',9);c.drawRightString(CW,y,f'月亮年齡加值 +{moon}');c.setFont('Emphasis',10)
                for j in range(count):c.rect(76+j*13,y-1,10,10,fill=0,stroke=1)
        else:
            for i,name in enumerate(['憤怒','羞愧','懷疑','恐懼']):
                x=i*CW/4;c.rect(x,12,10,10,fill=0,stroke=1);c.drawString(x+13,12,name)

def section_story(section,st):
    flow=[]
    if section.get('move'):flow.append(Paragraph('特色動作 / 起始取得' if section.get('signature') else '其他動作 / 起始再選一項',st['label']))
    flow.append(Paragraph(escape(section['title']),st['move'] if section.get('move') else st['heading']))
    for r in section['blocks']:
        text=r['text'];prefix='□ ' if r['field']=='bullets' else ''
        flow.append(Paragraph(prefix+safe(text),st['body']))
    if section['id']=='shadows':flow.insert(1,Tracks('shadows'))
    return flow

def height(story):return sum(f.wrap(CW,HEIGHT)[1]+f.getSpaceBefore()+f.getSpaceAfter() for f in story)
def draw_columns(c,left,right,book,page,size):
    for col,story in enumerate([left,right]):
        remaining=list(story);frame=Frame(M+col*(CW+GAP),BOTTOM,CW,HEIGHT,leftPadding=0,rightPadding=0,topPadding=0,bottomPadding=0);frame.addFromList(remaining,c)
        if remaining:raise ValueError(f'{book["id"]} page {page} column {col+1}: {len(remaining)} overflowing elements')
    audit.append({'playbook':book['id'],'page_in_playbook':page,'body_font_size':size,'columns_fit':True})

def decorate(c,b,page,total):
    c.setFillColor(INK);c.setFont('Title',25);c.drawString(M,H-42,b['title'])
    c.setFont('Body',10);c.drawString(M,H-60,b['en']+' / '+('核心' if b['edition']=='core' else '擴充')+'扮演書')
    c.setStrokeColor(GOLD);c.line(M,H-72,W-M,H-72)
    c.setFont('Body',8);c.setFillColor(INK);c.drawString(M,22,'龍族史詩 Epyllion · 非官方繁體中文校訂 · 2026-10-24')
    c.drawRightString(W-M,22,f'{b["title"]} {page}/2 · {total}')
    c.setTitle('Epyllion 繁體中文核心角色卡' if b['edition']=='core' else 'Epyllion 繁體中文擴充角色卡')
    c.setAuthor('Epyllion 原作 Marissa Kelly / Magpie Games；非官方中文校訂')

def page_stories(b,page,size):
    st=styles(size);sections={s['id']:s for s in b['sections']}
    if page==1:
        left=[Paragraph('名字：________________　色彩：________',st['body']),Paragraph('魅力：______　勇氣：______　機巧：______',st['body']),Spacer(1,5)]
        for sid in ['identity','creation','appearance','fellowship']:left+=section_story(sections[sid],st)
        growth=sections['growth']
        if b['id'] in ['orphan','rebel']:
            left+=section_story({'id':'growth-role','title':'你的成長差異','blocks':growth['blocks'][-1:]},st)
            growth=dict(growth,blocks=growth['blocks'][:-1])
        right=[Paragraph('經驗軌 / 填滿後選一項成長並清空',st['label']),Tracks('xp')]+section_story(growth,st)
        right+=[Spacer(1,10),Paragraph('五輪月亮 / 成年成長時劃掉一輪',st['label']),Paragraph('□ 虛無　□ 自由　□ 堅石　□ 靈魂　□ 風暴',st['body']),Spacer(1,10),Paragraph('友誼寶石 / 記下來自哪位夥伴及數量',st['label'])]
        for _ in range(3):right.append(Paragraph('____________________________________',st['body']))
        return left,right
    chunks=[section_story(s,st) for s in b['sections'] if s.get('move')]
    shadow=section_story(sections['shadows'],st)
    # Preserve move order, choose the least crowded column split.
    choices=[]
    for cut in range(1,5):
        left=section_story(sections['starting'],st)+[f for chunk in chunks[:cut] for f in chunk]
        right=[f for chunk in chunks[cut:] for f in chunk]+shadow
        choices.append((max(height(left),height(right)),left,right))
    _,left,right=min(choices,key=lambda x:x[0]);return left,right

for edition,name in [('core','epyllion-playbooks-zh.pdf'),('expansion','epyllion-ed-playbooks-zh.pdf')]:
    c=canvas.Canvas(str(OUT/name),pagesize=A4,pageCompression=1,invariant=1);page=0
    for b in [x for x in books if x['edition']==edition]:
        for local in [1,2]:
            page+=1
            for size in [10.7,10.4,10.1]:
                left,right=page_stories(b,local,size)
                if max(height(left),height(right))<=HEIGHT-5:break
            assert max(height(left),height(right))<=HEIGHT-5,(b['id'],local,height(left),height(right),HEIGHT)
            decorate(c,b,local,page);draw_columns(c,left,right,b,local,size);c.showPage()
    c.save();print(name,page,'pages')
manifest={'date':'2026-10-24','generator':'scripts/build-playbook-pdfs.py','canonical_content_sha256':digest(entries),'composition_sha256':digest(compose(entries)),'outputs':[],'layout_checks':audit}
for name in ['epyllion-playbooks-zh.pdf','epyllion-ed-playbooks-zh.pdf']:
    path=OUT/name;manifest['outputs'].append({'name':name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'bytes':path.stat().st_size})
(ROOT/'translation/playbook-pdf-build.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('All 20 pages fit two-column frames; canonical block composition validated.')
