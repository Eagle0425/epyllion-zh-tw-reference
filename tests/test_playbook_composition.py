import copy,pathlib,sys,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from quality_model import load
from playbook_model import compose,validate_composition
class PlaybookComposition(unittest.TestCase):
    @classmethod
    def setUpClass(cls):_,cls.entries,_=load();cls.books=compose(cls.entries)
    def test_all_ten_books_have_full_canonical_content(self):
        self.assertEqual(validate_composition(self.books,self.entries)['uncovered_blocks'],0)
        self.assertEqual([b['edition'] for b in self.books].count('expansion'),4)
    def test_signature_move_is_the_actual_starting_move(self):
        for b in self.books:
            signature=next(s for s in b['sections'] if s.get('signature'))
            self.assertTrue(signature['title'] in next(e for e in self.entries if e['id']==b['entry_id'])['paragraphs'][3 if b['edition']=='core' else 4])
    def test_omitting_an_option_fails_completeness(self):
        broken=copy.deepcopy(self.books);s=next(s for s in broken[0]['sections'] if s['id']=='appearance');s['blocks'].pop()
        with self.assertRaises(AssertionError):validate_composition(broken,self.entries)
    def test_missing_move_fails_completeness(self):
        broken=copy.deepcopy(self.books);broken[0]['sections']=[s for s in broken[0]['sections'] if not s.get('signature')]
        with self.assertRaises(AssertionError):validate_composition(broken,self.entries)
if __name__=='__main__':unittest.main()
