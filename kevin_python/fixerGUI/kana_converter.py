hira = '''が ぎ ぐ げ ご ざ じ ず ぜ ぞ だ ぢ づ で ど ば び ぶ べ ぼ ぱ ぴ ぷ ぺ ぽ
            あ い う え お か き く け こ さ し す せ そ た ち つ て と な に ぬ ね の
            は ひ ふ へ ほ ま み む め も や ゆ よ ら り る れ ろ わ を ん ぁ ぃ ぅ ぇ ぉ ゃ ゅ ょ っ'''
kata = '''ガ ギ グ ゲ ゴ ザ ジ ズ ゼ ゾ ダ ヂ ヅ デ ド バ ビ ブ ベ ボ パ ピ プ ペ ポ
            ア イ ウ エ オ カ キ ク ケ コ サ シ ス セ ソ タ チ ツ テ ト ナ ニ ヌ ネ ノ
            ハ ヒ フ ヘ ホ マ ミ ム メ モ ヤ ユ ヨ ラ リ ル レ ロ ワ ヲ ン ァ ィ ゥ ェ ォ ャ ュ ョ ッ'''

hira_list = hira.split()
kata_list = kata.split()
hiragana_to_katakana = {}
katakana_to_hiragana = {}

for h, k in zip(hira_list, kata_list):
    hiragana_to_katakana[h] = k
    katakana_to_hiragana[k] = h

def toHira( word ):
    temp = ""
    for character in word:
        temp += katakana_to_hiragana.get( character, character )
    return temp

def toKana( word ):
    temp = ""
    for character in word:
        temp += hiragana_to_katakana.get( character, character )
    return temp

