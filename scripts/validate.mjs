import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import {fileURLToPath} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..'),dist=path.join(root,'dist');
const ctx={window:{}};vm.runInNewContext(fs.readFileSync(path.join(dist,'data.js'),'utf8'),ctx);const d=ctx.window.EPYLLION;
const ids=new Set(),categories=new Set(['world','houses','creation','rules','moves','magic','shadow','growth','playbooks','playbook-moves','gm','gm-moves','first-session','hazards','examples','expansion','expansion-playbooks']);
const exists=f=>assert.ok(fs.statSync(path.join(dist,f)).isFile(),`Missing ${f}`);
const entries=d.entries;
for(const e of entries){assert.ok(!ids.has(e.id),`Duplicate ${e.id}`);ids.add(e.id);assert.ok(categories.has(e.category),`Unknown category ${e.category}`);assert.ok(e.title&&e.en&&e.kind&&e.source.pages&&e.source.book,`Incomplete ${e.id}`);assert.ok(e.paragraphs?.length||e.bullets?.length,`Empty ${e.id}`);assert.ok(d.sources[e.source.file],`Unknown source ${e.id}`);if(e.image)exists(e.image);assert.ok(!/\ufffd|TODO|PLACEHOLDER/i.test(JSON.stringify(e)),`Placeholder or broken encoding ${e.id}`);}
assert.equal(entries.filter(e=>e.category==='playbooks'&&e.role).length,6);
for(const role of Object.keys(d.roles))assert.equal(entries.filter(e=>e.role===role&&e.category==='playbook-moves').length,5,`${role} needs five moves`);
for(const id of ['study','help-hinder','moon-magic','shadow-magic','end-session','gems','shadows','shadowself'])assert.ok(ids.has(id),`Required rule ${id}`);
const study=entries.find(e=>e.id==='study').paragraphs.join('');assert.match(study,/10\+.*(兩|2).*7[–-]9.*(一|1)/,'Study questions reversed');
assert.match(entries.find(e=>e.id==='help-hinder').paragraphs.join(''),/[＋+]3/);
assert.equal(entries.filter(e=>e.category==='moves').length+2,9);
for(const s of Object.values(d.sources)){exists(s.path);const f=fs.readFileSync(path.join(dist,s.path));assert.equal(f.subarray(0,4).toString(),'%PDF',`Invalid PDF ${s.path}`);}
for(const f of ['index.html','gm.html','styles.css','app.js','assets/icon.svg','assets/group.webp','assets/epyllionmap2.webp'])exists(f);
new vm.Script(fs.readFileSync(path.join(dist,'app.js'),'utf8'));
assert.equal(d.stats.total,entries.length);
assert.equal(d.playbooks.length,10);
assert.equal(d.playbooks.filter(b=>b.edition==='expansion').length,4);
for(const b of d.playbooks){
 assert.equal(b.sections.filter(s=>s.move).length,5,`${b.id}: five inline moves required`);
 const pdf=d.sources[b.pdf_id];assert.ok(pdf&&b.pdf_page>=1&&b.pdf_page+1<=pdf.pdf_pages,`${b.id}: missing two-page Chinese PDF`);
 for(const s of b.sections)for(const r of s.blocks){const e=entries.find(e=>e.id===r.entry_id);assert.ok(e?.[r.field]?.[r.index],`${b.id}: invalid content reference`);}
}
const fonts=JSON.parse(fs.readFileSync(path.join(root,'translation/font-build.json'),'utf8'));
for(const f of fonts.fonts){exists(`assets/fonts/${f.output}`);const raw=fs.readFileSync(path.join(dist,'assets/fonts',f.output));assert.equal(raw.subarray(0,4).toString(),'wOF2');assert.equal(crypto.createHash('sha256').update(raw).digest('hex'),f.sha256);assert.equal(f.missing_cjk.length,0);}
exists('assets/fonts/OFL.txt');
console.log(`Validated ${entries.length} entries, ${Object.keys(d.sources).length} PDFs, ten complete playbooks / 50 inline moves and four local fonts. IDs, encoding, sources and rule checks passed.`);
