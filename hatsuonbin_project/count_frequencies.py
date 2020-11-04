import os
import speaker_record as r
from collections import defaultdict

f_word_recode_file = os.path.dirname(__file__) + "\\other_data\\f_word_recode.txt"

in_dir = os.path.dirname(__file__) + "\\corpus_data\\"
#in_dir = os.path.dirname(__file__) + "\\test\\"

discourse_list = ["やら","やから","や","やて","やー","やっ","やろ","やん","です","す","でし","だ","だっ","だろ","じゃ","じゃろ","で","ちゃう","ちゃん"]
sfp_list = ["な", "の","か","かい","よ","かも"]


morph_freq_file = os.path.dirname(__file__) + "\\other_data\\count_morph_freq.txt"
word_freq_file = os.path.dirname(__file__) + "\\other_data\\count_word_freq.txt"
morph_phrase_freq_file = os.path.dirname(__file__) + "\\other_data\\count_morph_phrase_freq.txt"
word_phrase_freq_file = os.path.dirname(__file__) + "\\other_data\\count_word_phrase_freq.txt"

morph_freq_dic = defaultdict(int)
word_freq_dic = defaultdict(int)
morph_phrase_freq_dic = defaultdict(int)
word_phrase_freq_dic = defaultdict(int)

f_word_recode_dic = {}
with open( f_word_recode_file, "r", encoding = "utf-8" ) as fh:
    data = fh.readlines()
for data_line in data:
    data_line = data_line.strip()
    following_word, recode = data_line.split("\t")
    f_word_recode_dic[ following_word ] = recode


files = os.listdir( in_dir )
for file in files:
    corpus = file[0:3]; speaker = file[0:6]; gender = file[6]; age = file[7]
    if corpus == "RGS":
        continue
    if age == "1": age = "10"
    print( file )
    full_file_name = in_dir + file
    fh_in = open( full_file_name, "r", encoding = "utf-8" )
    #leave p2 as blank initially since each record gets shift one as soon as the while loop starts
    p2 = r.Record()
    data_line = fh_in.readline()
    p1 = r.Record( data_line )
    data_line = fh_in.readline()
    current_record = r.Record( data_line )
    data_line = fh_in.readline()
    f1 = r.Record( data_line )
    data_line = fh_in.readline()
    f2 = r.Record( data_line )
    #########################

    #空い	動詞,自立,*,*,五段・カ行イ音便,連用タ接続,空く,アイ,アイ,s
    #てん	動詞,非自立,*,*,一段撥音便,基本形・縮約形,て＋いる,テン,テン,s

    #する/動詞/サ変・スル
    #してん/動詞--動詞
    #してる/動詞-助詞-動詞
    
    while True:
        p2 = p1; p1 = current_record; current_record = f1; f1 = f2
        data_line = fh_in.readline()
        if data_line == "": break
        f2 = r.Record( data_line )
      
        if current_record.record[1] == "動詞" and "基本形" in current_record.record[6] and current_record.record[7][-1] == "る" and f1.record[5] != "特殊・ナイ":

            #the word
            if current_record.record[2] == "非自立":
                if p1.record[0] == "て" or p1.record[0] == "で":
                    word = p2.record[0] + p1.record[0] + current_record.record[7]
                else:
                    word = p1.record[0] + current_record.record[7]
            else:
                word = current_record.record[7]
            word = word.replace("て＋いる", "てる")
            word = word.replace("て＋おる", "とる")
            word = word.replace("て＋あげる", "たげる")
            word = word.replace("て＋ある", "たる")

           
            #the morpheme
            morpheme = current_record.record[7]
            morpheme = morpheme.replace("て＋いる", "てる")
            morpheme = morpheme.replace("て＋おる", "とる")
            morpheme = morpheme.replace("て＋あげる", "たげる")
            morpheme = morpheme.replace("て＋ある", "たる")
            
            #the word phrase
            f_word = f1.record[0]
            f_word_recode = f_word_recode_dic.get( f_word, f_word )
            word_phrase = word + " " + f_word_recode + "/" + f1.record[1]

            #the morpheme phrase
            morpheme_phrase = morpheme +  " " + f_word_recode + "/" + f1.record[1]
        
            word_count = word_freq_dic[ word ] + 1
            word_freq_dic[ word ] = word_count

            morpheme_count = morph_freq_dic[ morpheme ] + 1
            morph_freq_dic[ morpheme ] = morpheme_count

            word_phrase_count = word_phrase_freq_dic[ word_phrase ] + 1
            word_phrase_freq_dic[ word_phrase ] = word_phrase_count

            morpheme_phrase_count = morph_phrase_freq_dic[ morpheme_phrase ] + 1
            morph_phrase_freq_dic[ morpheme_phrase ] = morpheme_phrase_count
            
    fh_in.close()

with open( word_freq_file, "w", encoding = "utf-8" ) as fh:
    fh.write("word\tcount\n")
    for word in word_freq_dic:
        word_count = word_freq_dic[  word ]
        fh.write("{}\t{}\n".format(word,word_count))

with open( morph_freq_file, "w", encoding = "utf-8" ) as fh:
    fh.write("morpheme\tcount\n")
    for morpheme in morph_freq_dic:
        morpheme_count = morph_freq_dic[  morpheme ]
        fh.write("{}\t{}\n".format(morpheme,morpheme_count))

with open( word_phrase_freq_file, "w", encoding = "utf-8" ) as fh:
    fh.write("word phrase\tcount\n")
    for word_phrase in word_phrase_freq_dic:
        word_phrase_count = word_phrase_freq_dic[ word_phrase ]
        fh.write("{}\t{}\n".format(word_phrase,word_phrase_count))

with open( morph_phrase_freq_file, "w", encoding = "utf-8" ) as fh:
    fh.write("morpheme phrase\tcount\n")
    for morpheme_phrase in morph_phrase_freq_dic:
        morpheme_phrase_count = morph_phrase_freq_dic[ morpheme_phrase ]
        fh.write("{}\t{}\n".format(morpheme_phrase,morpheme_phrase_count))

