import os
import speaker_record as r
import queue as q
import re
import math

test = False
#test = True

def logTen( x ):
    if x == "no data":
        return x
    else:
        y = math.log10( int( x ))
        z = round(y, 0)
        return z

def roundOffLogProb( x ):
    if x == "no data":
        return x
    else:
        y = float( x )
        z = round(y, 0)
        return z

if test:
    in_dir = os.path.dirname(__file__) + "\\test\\"
else:
    in_dir = os.path.dirname(__file__) + "\\corpus_data\\"

queue_size = 8

discourse_list = ["やら","やから","や","やて","やー","やっ","やろ","やん","です","す","でし","だ","だっ","だろ","じゃ","じゃろ","で","ちゃう","ちゃん"]
sfp_list = ["な", "の","か","かい","よ","かも"]

skip_list = ["KSJ015", "KSJ138", "KYT022"]


out_file = os.path.dirname(__file__) + "\\out_onbin.txt"
speech_style_file = os.path.dirname(__file__) + "\\other_data\\speech_style.txt"
f_word_recode_file = os.path.dirname(__file__) + "\\other_data\\f_word_recode.txt"
f_sound_recode_file = os.path.dirname(__file__) + "\\other_data\\f_sound_recode.txt"
wp_forw_prob_file = os.path.dirname(__file__) + "\\other_data\\ksj-vcompmerged-normal.srilm"
wp_back_prob_file = os.path.dirname(__file__) + "\\other_data\\ksj-vcompmerged-reverse.srilm"
mp_forw_prob_file = os.path.dirname(__file__) + "\\other_data\\ksj-normal-normal.srilm"
mp_back_prob_file = os.path.dirname(__file__) + "\\other_data\\ksj-normal-reverse.srilm"


morph_freq_file = os.path.dirname(__file__) + "\\other_data\\count_morph_freq.txt"
word_freq_file = os.path.dirname(__file__) + "\\other_data\\count_word_freq.txt"
morph_phrase_freq_file = os.path.dirname(__file__) + "\\other_data\\count_morph_phrase_freq.txt"
word_phrase_freq_file = os.path.dirname(__file__) + "\\other_data\\count_word_phrase_freq.txt"

speech_style_dic = {}
with open( speech_style_file, "r", encoding = "utf-8" ) as fh:
    data = fh.readlines()
for data_line in data:
    data_line = data_line.strip()
    speaker,index = data_line.split("\t")
    speech_style_dic[ speaker ] = index

f_word_recode_dic = {}
with open( f_word_recode_file, "r", encoding = "utf-8" ) as fh:
    data = fh.readlines()
for data_line in data:
    data_line = data_line.strip()
    following_word, recode = data_line.split("\t")
    f_word_recode_dic[ following_word ] = recode

f_sound_recode_dic = {}
with open( f_sound_recode_file, "r", encoding = "utf-8" ) as fh:
    data = fh.readlines()
for data_line in data:
    data_line = data_line.strip()
    kana, sound, nasal, place, voice, stricture = data_line.split("\t")
    f_sound_recode_dic[ kana ] = "{}\t{}\t{}\t{}\t{}".format(sound, nasal, place, voice, stricture)

morph_freq_dic = {}
with open( morph_freq_file, "r", encoding = "utf-8" ) as fh:
    data = fh.readlines()
for data_line in data:
    data_line = data_line.strip()
    morpheme,count = data_line.split("\t")
    morph_freq_dic[ morpheme ] = count

word_freq_dic = {}
with open( word_freq_file, "r", encoding = "utf-8" ) as fh:
    data = fh.readlines()
for data_line in data:
    data_line = data_line.strip()
    word,count = data_line.split("\t")
    word_freq_dic[ word ] = count

morph_phrase_freq_dic = {}
with open( morph_phrase_freq_file, "r", encoding = "utf-8" ) as fh:
    data = fh.readlines()
for data_line in data:
    data_line = data_line.strip()
    morpheme_phrase,count = data_line.split("\t")
    morph_phrase_freq_dic[ morpheme_phrase ] = count

word_phrase_freq_dic = {}
with open( word_phrase_freq_file, "r", encoding = "utf-8" ) as fh:
    data = fh.readlines()
for data_line in data:
    data_line = data_line.strip()
    word_phrase,count = data_line.split("\t")
    word_phrase_freq_dic[ word_phrase ] = count

morpheme_regex = r"(\-\d\.\d*)\t(.*?)\/(.*?)\/.*? (.*?)\/(.*?)\/" #(minus digit decimal digit-repeat) tab (char-repeat-nongreedy) space (char-repeat) backslash (char-repeat) backslash 
#-0.3077956	する/動詞/サ変・スル ねん/名詞/*
# returns -0.3077956, する, ねん, 名詞
#we want to then build する ねん/助詞

mp_forw_prob_dic = {}
with open( mp_forw_prob_file, "r", encoding = "utf-8" ) as fh:
    data = fh.readlines()
for data_line in data:
    data_line = data_line.strip()
    if re.search(morpheme_regex, data_line):
        match = re.search(morpheme_regex, data_line)
        probability = match.group(1)
        first_word = match.group(2)
        first_pos = match.group(3)
        second_word = match.group(4)
        second_pos = match.group(5)
        if (first_pos == "動詞" or first_pos == "助動詞") and second_pos != "記号":
            if first_word[-1] == "ん" or first_word[-1] == "る":
                first_word = first_word[:-1] + "る"
                morph_phrase = first_word + " " + second_word + "/" + second_pos
                old_probability = mp_forw_prob_dic.get( morph_phrase, 0)
                mp_forw_prob_dic[ morph_phrase ] = old_probability + float(probability)

mp_back_prob_dic = {}
with open( mp_back_prob_file, "r", encoding = "utf-8" ) as fh:
    data = fh.readlines()
for data_line in data:
    data_line = data_line.strip()
    if re.search(morpheme_regex, data_line):
        match = re.search(morpheme_regex, data_line)
        probability = match.group(1)
        #note that the order of the words is reversed
        second_word = match.group(2)
        second_pos = match.group(3)
        first_word = match.group(4)
        first_pos = match.group(5)
        if (first_pos == "動詞" or first_pos == "助動詞") and second_pos != "記号":
            if first_word[-1] == "ん" or first_word[-1] == "る":
                first_word = first_word[:-1] + "る"
                morph_phrase = first_word + " " + second_word + "/" + second_pos
                old_probability = mp_back_prob_dic.get( morph_phrase, 0)
                mp_back_prob_dic[ morph_phrase ] = old_probability + float(probability)

word_regex = r"(\-\d\.\d*)\t(.*?)\/(.*?) (.*?)\/(.*)" #(minus digit decimal digit-repeat) tab (char-repeat-nongreedy) space (char-repeat) backslash (char-repeat) backslash 
#-1.306012	覚えてる/動詞-助詞-動詞 けど/助詞/*	0.2039524
#want 覚えてる けど/助詞

wp_forw_prob_dic = {}
with open( wp_forw_prob_file, "r", encoding = "utf-8" ) as fh:
    data = fh.readlines()
for data_line in data:
    data_line = data_line.strip()
    if re.search(word_regex, data_line):
        match = re.search(word_regex, data_line)
        probability = match.group(1)
        first_word = match.group(2)
        first_pos = match.group(3)
        second_word = match.group(4)
        second_pos = match.group(5)
        word_phrase = first_word + " " + second_word + "/" + second_pos
        if "/" in first_pos:
            temp = first_pos.split("/")
        else:
            temp = first_pos.split("-")
        first_pos = temp[0]
        if "/" in second_pos:
            temp = second_pos.split("/")
        else:
            temp = second_pos.split("-")
        second_pos=temp[0]
        if (first_pos[0:2] == "動詞" or first_pos[0:3] == "助動詞") and second_pos != "記号":
            if first_word[-1] == "ん" or first_word[-1] == "る":
                first_word = first_word[:-1] + "る"
                word_phrase = first_word + " " + second_word + "/" + second_pos
                old_probability = wp_forw_prob_dic.get( word_phrase, 0)
                wp_forw_prob_dic[ word_phrase ] = old_probability + float(probability)

wp_back_prob_dic = {}
with open( wp_back_prob_file, "r", encoding = "utf-8" ) as fh:
    data = fh.readlines()
for data_line in data:
    data_line = data_line.strip()
    if re.search(word_regex, data_line):
        match = re.search(word_regex, data_line)
        probability = match.group(1)
        #note that the order of the words is reversed
        second_word = match.group(2)
        second_pos = match.group(3)
        first_word = match.group(4)
        first_pos = match.group(5)
        word_phrase = first_word + " " + second_word + "/" + second_pos
        if "/" in first_pos:
            temp = first_pos.split("/")
        else:
            temp = first_pos.split("-")
        first_pos = temp[0]
        if "/" in second_pos:
            temp = second_pos.split("/")
        else:
            temp = second_pos.split("-")
        second_pos=temp[0]
        if (first_pos[0:2] == "動詞" or first_pos[0:3] == "助動詞") and second_pos != "記号":
            if first_word[-1] == "ん" or first_word[-1] == "る":
                first_word = first_word[:-1] + "る"
                word_phrase = first_word + " " + second_word + "/" + second_pos
                old_probability = wp_back_prob_dic.get( word_phrase, 0)
                wp_back_prob_dic[ word_phrase ] = old_probability + float(probability)

context_q = q.Queue()

fh_out = open( out_file, "w", encoding = "utf-8" )
fh_out.write( "context\tcorpus\tspeaker\tage\tgender\tspeech_style\tonbin\tword\twPhrase\tmorph\tmPhrase\twFreq\tmFreq\twpFreq\tmpFreq\tadjacent\tf_word\tf_pos\ttraditional\tneutralized\twpfp\twpbp\tmpfp\tmpbp\n" )

files = os.listdir( in_dir )
for file in files:
    corpus = file[0:3]; speaker = file[0:6]; gender = file[6]; age = file[7]
    if corpus == "RGS":
        continue
    if speaker in skip_list:
        continue
    speech_style = speech_style_dic[ speaker ]
    if age == "1": age = "10"
    print( file )
    full_file_name = in_dir + file
    fh_in = open( full_file_name, "r", encoding = "utf-8" )
    #leave p2 as blank initially since each record gets shift one as soon as the while loop starts
    p2 = r.Record()
    data_line = fh_in.readline()
    p1 = r.Record( data_line )
    context_q.put( p1.record[0] )
    data_line = fh_in.readline()
    current_record = r.Record( data_line )
    context_q.put( current_record.record[0] )
    data_line = fh_in.readline()
    f1 = r.Record( data_line )
    context_q.put( f1.record[0] )
    data_line = fh_in.readline()
    f2 = r.Record( data_line )
    context_q.put( f2.record[0] )
    #########################
    while True:
        p2 = p1; p1 = current_record; current_record = f1; f1 = f2
        data_line = fh_in.readline()
        if data_line == "": break
        f2 = r.Record( data_line )
        if context_q.qsize() > queue_size:
            context_q.get()
        context_q.put( f2.record[0] )
      
        if current_record.speaker == "s" and current_record.record[1] == "動詞" and "基本形" in current_record.record[6] and current_record.record[7][-1] == "る" and f1.record[5] != "特殊・ナイ":

            ###hatsuonbin
            if "撥音便" in current_record.record[5]:
                onbin = "1"
            else:
                onbin = "0"
                
            ###word
            if current_record.record[2] == "非自立":
                adjacent = "0"
                if p1.record[0] == "て" or p1.record[0] == "で":
                    word = p2.record[0] + p1.record[0] + current_record.record[7]
                else:
                    word = p1.record[0] + current_record.record[7]
            else:
                adjacent = "1"
                word = current_record.record[7]
            #change て＋いる to てる, and て＋おる to とる
            word = word.replace("て＋いる", "てる")
            word = word.replace("て＋おる", "とる")
            word = word.replace("て＋あげる", "たげる")
            word = word.replace("て＋ある", "たる")

             ###morpheme
            morpheme = current_record.record[7]
            morpheme = morpheme.replace("て＋いる", "てる")
            morpheme = morpheme.replace("て＋おる", "とる")
            morpheme = morpheme.replace("て＋あげる", "たげる")
            morpheme = morpheme.replace("て＋ある", "たる")
            
            ###following word
            f_word = f1.record[0]
            f_word_recode = f_word_recode_dic.get( f_word, f_word ) #if found return the recoded f_word; if not found,return the original
                
            ###pos of following word
            if onbin == "O" and f1.record[0] in discourse_list and f1.record[2] != "終助詞":
                f_pos = "dis"
            elif f1.record[0] in ["ね", "ねん", "の", "のん", "ん", "が"] and f2.record[0] in discourse_list:
                f_pos = "dis"
            elif f1.record[0] in ["けど", "けどー", "けども"]:
                f_pos = "dis"
            elif f1.record[0] in ["ねん", "ね", "の", "ん"] and f2.record[0] in sfp_list:
                f_pos = "sfp"
            elif f1.record[0] in ["の", "のん", "ん"] and f2.record[0]:
                f_pos = "nom"
            elif f1.record[0] in ["みたい", "かも"]:
                f_pos = "dis"
            else:
                f_pos = f_word_recode_dic.get( f1.record[1]+f1.record[2], f1.record[1]+f1.record[2] ) #if found then return recoded pos; if not found, then return the original pos


            ###traditional context
            f_kana = f1.record[8][0] #the first kana of the following word
            f_phonology = f_sound_recode_dic.get( f_kana, "na\tna\tna\tna\tna" )
            #unpack the phonology of the following sound; for now only use the first item, "sound"
            sound, nasal, place, voice, stricture = f_phonology.split("\t")
            if (sound == "n" or sound == "d") and f_pos not in ["noun","other.lexical"]:
                traditional = "1"
            else:
                traditional = "0"

            ###word phrase
            word_phrase = word + " " + f_word_recode + "/" + f1.record[1]

            ###the morpheme phrase
            morpheme_phrase = morpheme +  " " + f_word_recode + "/" + f1.record[1]
            
            ###context
            context = ""
            while not context_q.empty():
                context += context_q.get()

            ###neutralized
            if f_word_recode == "ん":
                neutralized = "1"
            elif onbin == "1" and any([f_pos == "pause", f1.record[0] in discourse_list, f1.record[0] in ["は","が", "も", "って", "か", "かも"]]):
                neutralized = "1"
            else:
                neutralized = "0"
            if neutralized == "1" and traditional == "0":
                traditional = "1"
                
            ###back and forward probabilities
            if f_pos == "pause":
                wp_forw_prob = ""; wp_back_prob = ""; mp_forw_prob = ""; mp_back_prob =  ""
            else:
                mp_forw_prob = roundOffLogProb( mp_forw_prob_dic.get(morpheme_phrase, "no data") )
                mp_back_prob =  roundOffLogProb( mp_back_prob_dic.get(morpheme_phrase, "no data") )
                wp_forw_prob = roundOffLogProb( wp_forw_prob_dic.get(word_phrase, "no data") )
                wp_back_prob = roundOffLogProb( wp_back_prob_dic.get(word_phrase, "no data") )
                if wp_forw_prob == "no data" and mp_forw_prob != "no data":
                    wp_forw_prob = mp_forw_prob
                if wp_back_prob == "no data" and mp_back_prob != "no data":
                    wp_back_prob = mp_back_prob

            #frequencies
            word_freq = logTen( word_freq_dic.get(word, "no data"))
            morph_freq = logTen( morph_freq_dic.get(morpheme, "no data"))
            word_phrase_freq = logTen( word_phrase_freq_dic.get(word_phrase, "no data"))
            morph_phrase_freq = logTen( morph_phrase_freq_dic.get(morpheme_phrase, "no data"))

            output = "{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format( context, corpus, speaker, age, gender, speech_style,
                                                                                            onbin, word, word_phrase, morpheme, morpheme_phrase,
                                                                                            word_freq, morph_freq, word_phrase_freq, morph_phrase_freq,
                                                                                            adjacent, f_word_recode, f_pos, traditional, neutralized,
                                                                                            wp_forw_prob, wp_back_prob, mp_forw_prob, mp_back_prob )
            fh_out.write( output )

            
    fh_in.close()
fh_out.close()
