import os
import speaker_record as r
import queue as q



in_dir = os.path.dirname(__file__) + "\\corpus_data\\"
#in_dir = os.path.dirname(__file__) + "\\test\\"


queue_size = 8

#nominalizer_list = ["が","は","でも","も","とか","と","好き","嫌い","嫌","って"]
discourse_list = ["やら", "やから", "や","やっ","やろ","やん","です","でし","だ","だっ","だろ","じゃ","で","ちゃう","ちゃん"]
sfp_list = ["な", "の","か","かい","よ","かも"]

skip_list = ["KSJ015", "KSJ138", "KYT022"]


out_file = os.path.dirname(__file__) + "\\out_onbin.txt"
speech_style_file = os.path.dirname(__file__) + "\\other_data\\speech_style.txt"
f_word_recode_file = os.path.dirname(__file__) + "\\other_data\\f_word_recode.txt"
f_sound_recode_file = os.path.dirname(__file__) + "\\other_data\\f_sound_recode.txt"

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

context_q = q.Queue()


fh_out = open( out_file, "w", encoding = "utf-8" )
fh_out.write( "context\tcorpus\tspeaker\tword\tonbin\tage\tgender\tspeech_style\tlocation\tf_word\tf_pos\ttraditional\tneutralized\n" )

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
            if current_record.record[2] == "非自立":
                location = "nonadj"
                if p1.record[0] == "て" or p1.record[0] == "で":
                    word = p2.record[0] + p1.record[0] + current_record.record[7]
                else:
                    word = p1.record[0] + current_record.record[0]
            else:
                location = "adj"
                word = current_record.record[7]
            
            if "撥音便" in current_record.record[5]:
                onbin = "O"
            else:
                onbin = "X"
            f_word = f1.record[0]
            f_kana = f1.record[8][0] #the first kana of the following word
            #determine the f_pos
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
            f_word_recode = f_word_recode_dic.get( f_word, f_word ) #if found return the recoded f_word; if not found,return the original
            f_phonology = f_sound_recode_dic.get( f_kana, "na\tna\tna\tna\tna" )
            #unpack the fphonology of the following sound; for now only use the first item, "sound"
            sound, nasal, place, voice, stricture = f_phonology.split("\t")
            if sound == "n" or sound == "d":
                traditional = "O"
            else:
                traditional = "X"
            if f_pos == "pause":
                f_phrase = "."
            else:
                f2_word_recode = f_word_recode_dic.get( f2.record[0], f2.record[0] ) #if found return the recoded f_word; if not found,return the original
                f_phrase = f_word_recode + f2_word_recode
            context = ""
            #determine the phrase
            if current_record.record[0] == "る":
                phrase =  p1.record[7] + current_record.record[7] + f_word_recode
            else:
                phrase =  current_record.record[7] + f_word_recode
            #change て＋いる to てる
            phrase = phrase.replace("て＋いる", "てる")
            while not context_q.empty():
                context += context_q.get()
            if f_word_recode == "ん" or (onbin == "O" and f_pos == "pause"):
                neutralized = "O"
            else:
                neutralized = "X"
            output = "{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format( context, corpus, speaker, word, onbin, age, gender, speech_style, location, f_word_recode, f_pos, traditional, neutralized )
            #output = "{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format( corpus, speaker, age, gender, speech_style, word, aux, phrase, onbin, f_word_recode, f_pos, f_kana, f_phonology, f_phrase, context )
            fh_out.write( output )
            
    fh_in.close()
fh_out.close()
