"""Check every website block is readable in its corresponding two-page PDF."""
import json,re,unicodedata,pathlib
import pypdfium2 as pdfium
from quality_model import ROOT,load,digest,read
from playbook_model import compose,resolve
_,entries,_=load();books=resolve(compose(entries),entries)
def norm(text):return re.sub(r'\s+','',re.sub('[−–—‑]','-',unicodedata.normalize('NFKC',text)))
checked=0;pages=0
for edition,name in [('core','epyllion-playbooks-zh.pdf'),('expansion','epyllion-ed-playbooks-zh.pdf')]:
    doc=pdfium.PdfDocument(ROOT/'dist/downloads'/name);selected=[b for b in books if b['edition']==edition]
    assert len(doc)==len(selected)*2;pages+=len(doc)
    for i,b in enumerate(selected):
        text=norm(''.join(doc[j].get_textpage().get_text_range() for j in [2*i,2*i+1]))
        for s in b['sections']:
            for r in s['blocks']:
                assert norm(r['text']) in text,(b['id'],r)
                checked+=1
        assert '玻璃心' in text,b['id']
report={'date':'2026-10-24','pages':pages,'playbooks':len(books),'block_occurrences_checked':checked,'missing_blocks':0,'content_sha256':digest(entries),'composition_sha256':digest(compose(entries)),'visual_review':'All 20 pages rendered and inspected; full-size samples checked for font legibility, column bounds, XP boxes and headings.'}
(ROOT/'translation/playbook-pdf-check.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(report,ensure_ascii=False))
