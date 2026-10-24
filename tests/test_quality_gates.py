import json,pathlib,shutil,sys,tempfile,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from quality_check import check
class QualityGates(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory();cls.root=pathlib.Path(cls.temp.name)
        for name in ['content','translation']:shutil.copytree(ROOT/name,cls.root/name)
        (cls.root/'dist').mkdir();shutil.copyfile(ROOT/'dist/data.js',cls.root/'dist/data.js');shutil.copytree(ROOT/'dist/downloads',cls.root/'dist/downloads')
    @classmethod
    def tearDownClass(cls):cls.temp.cleanup()
    def setUp(self):self.backups={}
    def tearDown(self):
        for p,text in self.backups.items():p.write_text(text,encoding='utf-8')
    def edit(self,path,fn):
        p=self.root/path;self.backups.setdefault(p,p.read_text(encoding='utf-8'));d=json.loads(self.backups[p]);fn(d);p.write_text(json.dumps(d,ensure_ascii=False),encoding='utf-8')
    def test_baseline_does_not_claim_semantic_completion(self):
        r=check(self.root);self.assertTrue(r['structural_pass'])
        reviews=json.loads((self.root/'translation/reviews.json').read_text(encoding='utf-8'))['entries']
        self.assertEqual(r['semantic_pending'],sum(v['semantic_status']!='verified' for v in reviews.values()))
        if r['semantic_pending']:self.assertFalse(r['semantic_pass'])
    def test_changed_translation_invalidates_review_and_output(self):
        self.edit('content/rules.json',lambda d:d[0]['paragraphs'].__setitem__(0,d[0]['paragraphs'][0]+'（測試變更）'))
        errors=' '.join(check(self.root)['errors']);self.assertIn('review record is stale',errors);self.assertIn('data.js differs',errors)
    def test_pdf_pages_do_not_accept_printed_offset(self):
        self.edit('translation/provenance.json',lambda d:d['entries']['ed-credits']['pdf_ranges'][0].__setitem__('start',3))
        self.assertIn('page conversion',' '.join(check(self.root)['errors']))
    def test_page_bounds_are_enforced(self):
        self.edit('translation/provenance.json',lambda d:d['entries']['ed-credits']['pdf_ranges'][0].__setitem__('end',9999))
        self.assertIn('outside PDF bounds',' '.join(check(self.root)['errors']))
    def test_verified_review_requires_evidence(self):
        self.edit('translation/reviews.json',lambda d:d['entries']['study'].__setitem__('semantic_status','verified'))
        self.assertIn('lacks reviewer/evidence',' '.join(check(self.root)['errors']))
    def test_strict_semantic_gate_remains_separate(self):
        r=check(self.root,require_semantic=True);self.assertTrue(r['structural_pass']);self.assertFalse(r['gate_pass']);self.assertFalse(r['semantic_pass'])
    def test_unlisted_files_cannot_be_silently_published(self):
        p=self.root/'content/unlisted.json';p.write_text('[]',encoding='utf-8')
        try:self.assertIn('Unlisted or missing',' '.join(check(self.root)['errors']))
        finally:p.unlink()
    def test_artifact_hashes_are_checked(self):
        self.edit('translation/artifacts.json',lambda d:d['artifacts'][0].__setitem__('sha256','0'*64))
        self.assertIn('artifact changed',' '.join(check(self.root)['errors']))
if __name__=='__main__':unittest.main()
