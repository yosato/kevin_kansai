import unittest,imp,sys,os
from pdb import set_trace

import clean_twitter
imp.reload(clean_twitter)

TestPairs=[
    ('やったあああああ',['やったあ']),
    ('はーい☀わかった',['はあい わかった']),
    ('ははは~~〜〜〜',['はははー']),
    ('最新芸能今だニュース&amp;芸能ウラペディア』https://t',['最新芸能今だニュース&amp;芸能ウラペディア』']),
]

class TestCleanLine(unittest.TestCase):
    def setUp(self):
        self.testpairs=TestPairs

    def test_clean_line_with_defaults(self):
        for (OrgLine,ExpNewLines) in self.testpairs:
            set_trace()
            ResNewLines=clean_twitter.clean_line_with_defaults(OrgLine,Debug=1)
            self.assertEqual(ResNewLines,ExpNewLines)

if __name__=='__main__':
    unittest.main()
