import unittest,imp
from pdb import set_trace
import eval_mecab
imp.reload(eval_mecab)

class TestEvalMecab(unittest.TestCase):
    def setUp(self):
        self.Pair1=(
            ['批判\t名詞,サ変接続,*,*,*,*,批判,ヒハン,ヒハン', '的\t名詞,接尾,形容動詞語幹,*,*,*,的,テキ,テキ', 'に\t助詞,副詞化,*,*,*,*,に,ニ,ニ', 'なり\t動詞,自立,*,*,五段・ラ行,連用形,なる,ナリ,ナリ', '過ぎ\t動詞,非自立,*,*,一段,連用形,過ぎる,スギ,スギ', 'て\t助詞,接続助詞,*,*,*,*,て,テ,テ', 'も\t助詞,係助詞,*,*,*,*,も,モ,モ', '世の中\t名詞,一般,*,*,*,*,世の中,ヨノナカ,ヨノナカ', '上手く\t形容詞,自立,*,*,形容詞・アウオ段,連用テ接続,上手い,ウマク,ウマク', 'いか\t動詞,自立,*,*,五段・カ行促音便,未然形,いく,イカ,イカ', 'へん\t助動詞,*,*,*,不変化型,基本形,へん,ヘン,ヘン', 'やん\t助動詞,*,*,*,不変化型,基本形,やん,ヤン,ヤン', 'か\t助詞,副助詞／並立助詞／終助詞,*,*,*,*,か,カ,カ', '。\t記号,句点,*,*,*,*,。,。,。'],
             ['====', '@1', '批判\t名詞,サ変接続,*,*,*,*,批判,ヒハン,ヒハン', '的\t名詞,接尾,形容動詞語幹,*,*,*,的,テキ,テキ', '@2', '批判的\t名詞,形容動詞語幹,*,*,*,*,批判的,ヒハンテキ,ヒハンテキ', '====', 'に\t助詞,格助詞,一般,*,*,*,に,ニ,ニ', 'なり\t動詞,自立,*,*,五段・ラ行,連用形,なる,ナリ,ナリ', '過ぎ\t動詞,非自立,*,*,一段,連用形,過ぎる,スギ,スギ', 'て\t助詞,接続助詞,*,*,*,*,て,テ,テ', 'も\t助詞,係助詞,*,*,*,*,も,モ,モ', '====', '@1', '世\t名詞,一般,*,*,*,*,世,ヨ,ヨ', 'の\t助詞,連体化,*,*,*,*,の,ノ,ノ', '中\t名詞,非自立,副詞可能,*,*,*,中,ナカ,ナカ', '@2', '世の中\t名詞,一般,*,*,*,*,世の中,ヨノナカ,ヨノナカ', '====', '上手く\t形容詞,自立,*,*,形容詞・アウオ段,連用テ接続,上手い,ウマク,ウマク', 'いか\t動詞,非自立,*,*,五段・カ行促音便,未然形,いく,イカ,イカ', 'へん\t助動詞,*,*,*,特殊・ナイ,基本形,へん,ヘン,ヘン', 'やん\t助動詞,*,*,*,特殊・ヤ,基本形,や,ヤン,ヤン', 'か\t助詞,副助詞／並立助詞／終助詞,*,*,*,*,か,カ,カ', '。\t記号,句点,*,*,*,*,。,。,。'],
            ([0,4,9],[14,14]),([0,4,8],[14,16])
        )
        self.Pair2=(
            ['だから\t接続詞,*,*,*,*,*,だから,ダカラ,ダカラ', '全然\t副詞,助詞類接続,*,*,*,*,全然,ゼンゼン,ゼンゼン', 'うち\t名詞,非自立,副詞可能,*,*,*,うち,ウチ,ウチ', '信じ\t動詞,自立,*,*,一段,未然形,信じる,シンジ,シンジ', 'ひん\t助動詞,*,*,*,不変化型,基本形,ひん,ヒン,ヒン', 'もん\t助詞,終助詞,*,*,*,*,もん,モン,モン', '。\t記号,句点,*,*,*,*,。,。,。'],
            ['だから\t接続詞,*,*,*,*,*,だから,ダカラ,ダカラ', '全然\t副詞,助詞類接続,*,*,*,*,全然,ゼンゼン,ゼンゼン', 'うち\t名詞,代名詞,一般,*,*,*,うち,ウチ,ウチ', '信じ\t動詞,自立,*,*,一段,未然形,信じる,シンジ,シンジ', 'ひん\t助動詞,*,*,*,特殊・ナイ,基本形・母音調和,へん,ヒン,ヒン', '====', '@1', 'もん\t名詞,非自立,一般,*,*,*,もん,モン,モン', '@2', 'もん\t助詞,終助詞,*,*,*,*,もん,モン,モン', '====', '。\t記号,句点,*,*,*,*,。,。,。'],
            ([0,2,5],[7,7]),([1,2,4],[7,7])
            )
        self.Pair3=(
            ['何で\t副詞,一般,*,*,*,*,何で,ナンデ,ナンデ', 'で\t動詞,自立,*,*,一段,連用形,でる,デ,デ', 'て\t助詞,接続助詞,*,*,*,*,て,テ,テ', 'こ\t動詞,非自立,*,*,カ変・クル,未然形,くる,コ,コ', 'や\t助動詞,*,*,*,特殊・ヤ,基本形,や,ヤ,ヤ', 'へん\t名詞,非自立,一般,*,*,*,へん,ヘン,ヘン', 'か\t助詞,副助詞／並立助詞／終助詞,*,*,*,*,か,カ,カ', 'って\t助詞,格助詞,連語,*,*,*,って,ッテ,ッテ', 'ん\t名詞,非自立,一般,*,*,*,ん,ン,ン', 'やろ\t助動詞,*,*,*,特殊・ヤ,未然形,や,ヤロ,ヤロ', '。\t記号,句点,*,*,*,*,。,。,。'],
            ['何で\t副詞,一般,*,*,*,*,何で,ナンデ,ナンデ', 'で\t動詞,自立,*,*,一段,連用形,でる,デ,デ', 'て\t助詞,接続助詞,*,*,*,*,て,テ,テ', 'こや\t動詞,自立,*,*,カ変・クル,未然形・や挿入,くる,コヤ,コヤ', 'へんかっ\t助動詞,*,*,*,特殊・ナイ,連用タ接続,へん,ヘンカッ,ヘンカッ', '====', '@1', 'て\t助動詞,*,*,*,特殊・タ,基本形・母音変化,た,テ,テ', 'ん\t名詞,非自立,一般,*,*,*,ん,ン,ン', '@2', 'てん\t助動詞,*,*,*,特殊・タ＋んや,基本形・縮約形,てん,テン,テン', '====', 'やろ\t助動詞,*,*,*,特殊・ヤ,未然形,や,ヤロ,ヤロ', '。\t記号,句点,*,*,*,*,。,。,。'],
            ([0,0,5],[11,9]),([0,0,5],[11,9])
            )
#        self.Pair4=(
#            ['ラグビー\t名詞,一般,*,*,*,*,ラグビー,ラグビー,ラグビー', '部\t名詞,接尾,一般,*,*,*,部,ブ,ブ', '、\t記号,読点,*,*,*,*,、,、,、', '中学\t名詞,一般,*,*,*,*,中学,チュウガク,チューガク', 'ラグビー\t名詞,一般,*,*,*,*,ラグビー,ラグビー,ラグビー', '部\t名詞,接尾,一般,*,*,*,部,ブ,ブ', '一\t名詞,数,*,*,*,*,一,イチ,イチ', '人\t名詞,接尾,助数詞,*,*,*,人,ニン,ニン', 'しか\t助詞,係助詞,*,*,*,*,しか,シカ,シカ', 'いて\t動詞,自立,*,*,一段,未然形,いてる,イテ,イテ', 'へん\t助動詞,*,*,*,不変化型,基本形,へん,ヘン,ヘン', 'か\t助詞,副助詞／並立助詞／終助詞,*,*,*,*,か,カ,カ', 'って\t助詞,格助詞,連語,*,*,*,って,ッテ,ッテ', 'ん\t名詞,非自立,一般,*,*,*,ん,ン,ン', '。\t記号,句点,*,*,*,*,。,。,。'],
#            ['ラグビー\t名詞,一般,*,*,*,*,ラグビー,ラグビー,ラグビー', '部\t名詞,接尾,一般,*,*,*,部,ブ,ブ', '、\t記号,読点,*,*,*,*,、,、,、', '中学\t名詞,一般,*,*,*,*,中学,チュウガク,チューガク', 'ラグビー\t名詞,一般,*,*,*,*,ラグビー,ラグビー,ラグビー', '部\t名詞,接尾,一般,*,*,*,部,ブ,ブ', '一人\t名詞,一般,*,*,*,*,一人,ヒトリ,ヒトリ', 'しか\t助詞,係助詞,*,*,*,*,しか,シカ,シカ', 'い\t動詞,自立,*,*,一段,連用形,いる,イ,イ', 'て\t助詞,接続助詞,*,*,*,*,て,テ,テ', 'へんかっ\t助動詞,*,*,*,特殊・ナイ,連用タ接続,へん,ヘンカッ,ヘンカッ', '====', '@1', 'て\t助動詞,*,*,*,特殊・タ,基本形・母音変化,た,テ,テ', 'ん\t名詞,非自立,一般,*,*,*,ん,ン,ン', '@2', 'てん\t助動詞,*,*,*,特殊・タ＋んや,基本形・縮約形,てん,テン,テン', '====', '。\t記号,句点,*,*,*,*,。,。,。'],
#            ([0,2,5],[15,]),([1,2,4],[15,])
#        )
        set_trace()
        #Pair=eval_mecab.process_chunk(self.Pair1)
        RawPairs=[(RawPair[0],RawPair[1],RawPair[2]) for RawPair in (self.Pair1,self.Pair2,self.Pair3)]
        self.Pairs=[ (eval_mecab.process_chunk(RawPair[0]),eval_mecab.process_chunk(RawPair[1]),RawPair[2]) for RawPair in RawPairs]
        
        
    def test_score_sent(self):
        set_trace()
        for Pair in self.Pairs:
            AllegedScore=eval_mecab.score_sent(Pair[0],Pair[1])
            RealScore=Pair[2]
            self.assertEqual(AllegedScore,RealScore)

if __name__=='__main__':
    unittest.main()

