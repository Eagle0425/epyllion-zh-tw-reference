"""Subset the user-provided, OFL-licensed fonts; preserve source font files."""
import argparse,hashlib,json,pathlib,shutil,sys,logging
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'.font-deps'))
from fontTools import subset
from fontTools.ttLib import TTFont
parser=argparse.ArgumentParser();parser.add_argument('--font-directory',type=pathlib.Path,required=True);args=parser.parse_args()
dest=ROOT/'dist/assets/fonts';dest.mkdir(parents=True,exist_ok=True)
text=''.join(p.read_text(encoding='utf8') for p in [* (ROOT/'content').glob('*.json'),ROOT/'dist/app.js',ROOT/'dist/index.html',ROOT/'dist/gm.html',ROOT/'scripts/playbook_model.py'])+''.join(map(chr,range(32,127)))+'□☾◇✦☆★◎⚑✎♧♜◔☷⌂↗←→−＋①②③'
records=[];logging.getLogger('fontTools').setLevel(logging.ERROR)
for original,name,role in [('JasonHandwriting1-SemiBold.ttf','jason-title','角色與頁面大標'),('JasonHandwriting1-Medium.ttf','jason-section','區塊標題'),('JasonHandwriting2-SemiBold.ttf','jason-emphasis','小標、導覽與重點'),('JasonHandwriting2-Regular.ttf','jason-body','正文與輔助資訊')]:
 source=args.font_directory/original;font=TTFont(source);cmap=font.getBestCmap();missing=sorted({c for c in text if 0x3400<=ord(c)<=0x9fff and ord(c) not in cmap})
 assert not missing,(name,missing)
 options=subset.Options();options.flavor='woff2';options.name_IDs=['*'];options.name_legacy=True;options.name_languages=['*'];options.notdef_glyph=True;options.notdef_outline=True
 sub=subset.Subsetter(options=options);sub.populate(text=text);sub.subset(font);font.flavor='woff2';font.save(dest/f'{name}.woff2')
 records.append({'original':original,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'output':f'{name}.woff2','sha256':hashlib.sha256((dest/f'{name}.woff2').read_bytes()).hexdigest(),'bytes':(dest/f'{name}.woff2').stat().st_size,'purpose':role,'missing_cjk':missing})
shutil.copyfile(args.font_directory/'SIL_Open_Font_License_1.1.txt',dest/'OFL.txt')
(dest/'README.md').write_text('# 網站字體\n\n使用工作區提供的 JasonHandWritingFonts，依原字型配置分配四種用途。來源：https://github.com/max32002/JasonHandWritingFonts 。依 SIL OFL 1.1 授權（見 OFL.txt）產生 WOFF2 子集，保留原始版權與字型命名資訊。原始 TTF 未修改。\n\n中文字檢查涵蓋網站全部正文；符號可使用系統字體後備。新增正文後請重新執行 scripts/build-fonts.py。\n',encoding='utf8')
(ROOT/'translation/font-build.json').write_text(json.dumps({'date':'2026-10-24','fonts':records},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(records,ensure_ascii=False))
