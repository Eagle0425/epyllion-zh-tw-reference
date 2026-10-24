"""Generate the reader without altering translations."""
from quality_model import ROOT,data_js,load
_,entries,_=load(ROOT)
(ROOT/'dist/data.js').write_text(data_js(ROOT),encoding='utf-8')
index=(ROOT/'dist/index.html').read_text(encoding='utf-8')
(ROOT/'dist/gm.html').write_text(index.replace('<title>龍族史詩 Epyllion｜繁體中文手冊</title>','<title>龍主工作台｜龍族史詩 Epyllion</title>'),encoding='utf-8')
(ROOT/'dist/.nojekyll').write_text('',encoding='utf-8')
print(f'Generated {len(entries)} canonical entries. No terminology substitutions performed.')
