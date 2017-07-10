import tkinter as tk
from tkinter import scrolledtext as sctxt
from tkinter import ttk
import re
from os import listdir, getcwd
from threading import Thread
import pickle
from collections import namedtuple


###GLOBAL VARIABLES###

Morpheme = namedtuple("Morpheme", "morpheme voice d1 d2 d3 d4 d5 d6 d7")
FILE_DIR = getcwd() + "\\data_tpl\\"
FILE_NAME_PATTERN = re.compile( r"(...)(...)([FM])(\d{1,2})\.tpl" )
#extract four groups: 1. three characters; 2. three characters; 3. either F or M; 4. 1 or 2 digit characters
CORPORA = [("KSJ", "大阪周辺"), ("TKC", "多可町"), ("KYT", "京都"), ("RGS", "留学生")]
AGE = [("2", "高校生"), ("3", "大学生"), ("4", "24才-29才"), ("5", "30才-39才"), ("6", "40才-49才"), ("7", "50才-59才"), ("8", "60才-69才"), ("9", "70才-79才"), ("10", "80才-89才")]
SEX = [("F", "女性"), ("M", "男性"), ("FM", "両方")] 
VOICE = [("s", "話者のみ"), ("i", "インタビューアのみ"), ("si", "両方")]
POS = ["未定", "名詞", "動詞", "副詞", "形容詞", "助動詞", "助詞", "感動詞", "接続詞", "接頭詞", "連体詞", "フィラー", "記号"]

###SPEAKER OBJECTS###
class Corpus():
    '''A dictionary list of all speakers
    The keys are: code + number + gender + age
    Example: KSJ001F3
    The speakers are objects'''
    def __init__( self ):
        #a dictionary list of speaker objects
        self.list = {}

    def __repr__( self ):
        #returns the keys from the dictionary list of speaker objects
        #conversts the keys to strings before returning them
        temp = ""
        for s in self.list.keys():
            temp += str( s ) + "\n"
        return temp

    def addSpeaker( self, speaker, key ):
        #add speaker object with key to the dictionary list of speaker objects
        self.list[key] =  speaker

    def getList( self ):
        #return a sorted list containing all of the keys in the dic self.list
        l = list( self.list.keys() )
        l.sort()
        return l

    def getSpeaker( self, key ):
        #get the speaker object for the specified key
        return self.list[key]

class Speaker():
    '''Object with the following:
    data: corpus, number, sex, age
    fuctions: getInterview'''
   
    def __init__( self, corpus, number, sex, age ):
        #set up a new speaker object with the data: corpus, number, sex, age
        self.corpus = corpus
        self.number = number
        self.sex = sex
        self.age = age

    def __repr__( self ):
        #return a string such as KSJ003F4
        return str( "{}{}{}{}".format(self.corpus, self.number, self.sex, self.age) )

    def getInterview ( self, voice, speechOnly ):
        '''This is an object method that get the interview data of self
        Return either the full pos data, or just the interview transcription, depending on the speechOnly parameter
        Return the interview for either the interviewer, the speaker, or both, depending on the voice parameter
        voice is either [s]peaker, [i]nterviewer, or [si] both 
        speechOnly=True: returns a single string
        speechOnly=False: returns a list of morpheme tuples'''
        file_name = FILE_DIR + self.__repr__() + ".tpl"
        try:
            fh = open(file_name, "rb") #read-only, binary mode
            buffer = pickle.load( fh ) #load all of the pickles into buffer
            fh.close()
        except IOError:
            self.output_box.insert(tk.END, "\n\入力ファイルを開けることが出来ません。ファイル名：{}\n行動を中止します。\n".format( file_name) )
        else:
            if speechOnly:
                interview = ""
                for item in buffer:
                    #Does the voice variable match the morpheme tuple?
                    #item.voice is the second record, i.e., one of [i, s, i2, s2, .]
                    if (item.voice in voice):
                        interview += item.morpheme
            else:
                interview = []
                for item in buffer:
                    if (item.voice in voice):
                        interview.append( item )
            return interview

class InputTracker():
    '''Tracks the status and contents of all of the check boxes and entry boxes
    This is done inside dictionaries
    self.corpus[corpus_tkVar] is the tk variable linked to the self.corpus[corpus_widget]
    self.corpus[corpus_widget].get() returns the status of the checkbox

    List of widget interface commands:
     user_input.corpus["..._tkVar"].get(); where ... is one of CORPORA
     user_input.age["..._tkVar"].get(); where ... is one of AGE
     user_input.sex["sex_tkVar"].get()
     user_input.voice["voice_tkVar"].get()
     user_input.save_file["file_name_tkVar"].get()
     user_input.save_file["delimiter_tkVar"].get()
     user_input.search_expression["expression_tkVar"].get()
     user_input.search_expression["front_tkVar"].get() #front padding
     user_input.search_expression["back_tkVar"].get() #back padding
     user_input.search_morpheme["morpheme..._tkVar"]; where ... is one of 11, 12, 13, 21, 21, 22, 23, 31, 32, 33
     user_input.search_morpheme["morpheme..._pos_tkVar"]; where ... is one of 11, 12, 13, 21, 21, 22, 23, 31, 32, 33
     '''
        
    def __init__( self ):
        self.corpus = {}
        self.age = {}
        self.sex = {}
        self.voice = {}
        self.save_file = {}
        self.search_expression = {}
        self.search_morpheme = {}
        
    def getLimitedSpeakerList( self ):
        '''return a list of speakers that match the user selection paramaters
        Example: the the user selected only the female foreign students, then return
        a list containing only those speakers'''
        candidate_list = []
        for s in speaker_list.getList():
            candidate = speaker_list.getSpeaker( s )
            isCorpusOK = user_input.corpus[candidate.corpus + "_tkVar"].get()
            isAgeOK = user_input.age[candidate.age + "_tkVar"].get()
            isSexOK = candidate.sex in user_input.sex["sex_tkVar"].get()
            if (isCorpusOK and isAgeOK and isSexOK): candidate_list.append( str(s) )
        return candidate_list

class Interface():
    '''object with
    data: none
    methods: build, start'''

    #set up a dictionary that converts the corpus, age, sex and voice values into easy-to-read strings, e.g., "2" -> "高校生"
    convert_to_string = {}
    for tuple_pair in CORPORA:
        convert_to_string[ tuple_pair[0] ] = tuple_pair[1]
    for tuple_pair in AGE:
        convert_to_string[ tuple_pair[0] ] = tuple_pair[1]
    for tuple_pair in SEX:
        convert_to_string[ tuple_pair[0] ] = tuple_pair[1]
    for tuple_pair in VOICE:
        convert_to_string[ tuple_pair[0] ] = tuple_pair[1]

    def __init__( self ):
        self.win = tk.Tk()
        self.win.title("関西弁コーパス")
        self.win.resizable(0, 0)

    def atLeast( self, value, lower_limit ):
        '''check to see if a value is at least as big as a lower limit
        if it is, then return that value
        otherwise, return the lower limit'''
        if value < lower_limit: return lower_limit
        else: return value

    def atMost( self, value, upper_limit ):
        '''check to see if a value is at least as small as an upper limit
        if it is, then return that value
        otherwise, return the upper limit'''
        if value > upper_limit: return upper_limit
        else: return value
  
    def build( self ):
        pad_x = 10; pad_y = 5
        #frame 3: message output
        frame3 = ttk.LabelFrame( self.win, text="メッセージ出力", borderwidth=18 )
        frame3.grid( column=0, row=1, padx=pad_x, pady=pad_y, sticky=tk.W )
        self.addOutputBox( frame3 )
        
        #frame 1: speaker characteristics
        frame1 = ttk.LabelFrame( self.win, text="話し手選択", borderwidth=10 )
        frame1.grid( column=0, row=0, padx=pad_x, pady=pad_y, sticky=tk.W )
        self.addCheckBoxes( 0, 1, frame1, "コーパス", user_input.corpus, CORPORA )
        self.addCheckBoxes( 0, 2, frame1, "年齢", user_input.age, AGE )
        self.addRadioButtons( 0, 3, frame1, "性別", user_input.sex, SEX, "sex" )
        self.addRadioButtons( 0, 4, frame1, "何方の発話", user_input.voice, VOICE, "voice" )

        #frame 2:  search
        #contains frames 21 and 22
        #frame 21 contains frame2a (entry box), frame2b (padding), and frame2c (action button)
        frame2 = ttk.LabelFrame( self.win, text="検索", borderwidth=10 )
        frame2.grid( column=1, row=0, padx=pad_x, pady=pad_y, sticky=tk.W )
        frame21 = ttk.LabelFrame( frame2, text="表現検索", borderwidth=10 )
        frame21.grid( column=0, row=0, padx=pad_x, pady=pad_y, sticky=tk.W )
        frame2a = ttk.LabelFrame( frame21, text="表現入力", borderwidth=5 )
        frame2a.grid( column=0, row=0 )
        frame2b = ttk.LabelFrame( frame21, text="前後の字数", borderwidth=5 )
        frame2b.grid( column=1, row=0 )
        frame2c = ttk.LabelFrame( frame21, borderwidth=5 )
        frame2c.grid( column=2, row=0 )
        self.addEntryBox( 0, 0, frame2a, "表現: ", user_input.search_expression, "expression", 12, "" )
        self.addSpinBox( 2, 0, frame2b, "前: ", user_input.search_expression, "front",  2, 1, 30)
        self.addSpinBox( 4, 0, frame2b, "後ろ: ", user_input.search_expression, "back",  2, 1, 30)
        expression_start_button = ttk.Button(frame2c, text="開始", command=self.createSearchExpressionThread)
        expression_start_button.grid(column=6, row=0)
        
        #frame 22 contains frame2d (search tabs) and frame2e (action button)
        frame22 = ttk.LabelFrame( frame2, text="形態素検索", borderwidth=10 )
        frame22.grid( column=0, row=1, padx=pad_x, pady=pad_y, sticky=tk.W )
        widget_width = 8
        frame2d = ttk.LabelFrame( frame22, borderwidth=5 )
        frame2d.grid( column=0, row=0 )
        frame2e = ttk.LabelFrame( frame22, borderwidth=5 )
        frame2e.grid( column=1, row=0 )
        morpheme_start_button = ttk.Button(frame2e, text="開始", command=self.createSearchMorphemeThread)
        morpheme_start_button.grid(column=0, row=0)

        tabControl = ttk.Notebook(  frame2d, padding = 5 )
        tab1 = ttk.Frame( tabControl )
        tabControl.add( tab1, text = '　第一位　', padding = 5 )
        tabControl.pack( expand=1, fill="both" )
        self.addEntryBox( 0, 0, tab1, "  変異形1: ", user_input.search_morpheme, "morpheme11", widget_width, "" )
        self.addEntryBox( 0, 1, tab1, "  変異形2: ", user_input.search_morpheme, "morpheme12", widget_width, "" )
        self.addEntryBox( 0, 2, tab1, "  変異形3: ", user_input.search_morpheme, "morpheme13", widget_width, "" )
        self.addComboBox( 2, 0, tab1, "    品詞: ", user_input.search_morpheme, "morpheme11_pos", widget_width, POS )
        self.addComboBox( 2, 1, tab1, "    品詞: ", user_input.search_morpheme, "morpheme12_pos", widget_width, POS )
        self.addComboBox( 2, 2, tab1, "    品詞: ", user_input.search_morpheme, "morpheme13_pos", widget_width, POS )
        
        tab2 = ttk.Frame( tabControl )
        tabControl.add( tab2, text = '　第二位　', padding = 5 )
        tabControl.pack( expand=1, fill="both" )
        self.addEntryBox( 0, 0, tab2, "  変異形1: ", user_input.search_morpheme, "morpheme21", widget_width, "" )
        self.addEntryBox( 0, 1, tab2, "  変異形2: ", user_input.search_morpheme, "morpheme22", widget_width, "" )
        self.addEntryBox( 0, 2, tab2, "  変異形3: ", user_input.search_morpheme, "morpheme23", widget_width, "" )
        self.addComboBox( 2, 0, tab2, "    品詞: ", user_input.search_morpheme, "morpheme21_pos", widget_width, POS )
        self.addComboBox( 2, 1, tab2, "    品詞: ", user_input.search_morpheme, "morpheme22_pos", widget_width, POS )
        self.addComboBox( 2, 2, tab2, "    品詞: ", user_input.search_morpheme, "morpheme23_pos", widget_width, POS )
        
        tab3 = ttk.Frame( tabControl )
        tabControl.add( tab3, text = '　第三位　', padding = 5 )
        tabControl.pack( expand=1, fill="both" )
        self.addEntryBox( 0, 0, tab3, "  変異形1: ", user_input.search_morpheme, "morpheme31", widget_width, "" )
        self.addEntryBox( 0, 1, tab3, "  変異形2: ", user_input.search_morpheme, "morpheme32", widget_width, "" )
        self.addEntryBox( 0, 2, tab3, "  変異形3: ", user_input.search_morpheme, "morpheme33", widget_width, "" )
        self.addComboBox( 2, 0, tab3, "    品詞: ", user_input.search_morpheme, "morpheme31_pos", widget_width, POS )
        self.addComboBox( 2, 1, tab3, "    品詞: ", user_input.search_morpheme, "morpheme32_pos", widget_width, POS )
        self.addComboBox( 2, 2, tab3, "    品詞: ", user_input.search_morpheme, "morpheme33_pos", widget_width, POS )

        #frame 4: save file name
        frame4 = ttk.LabelFrame( self.win, text="出力ファイル", borderwidth=10 )
        frame4.grid( column=1, row=1, padx=pad_x, pady=pad_y, sticky=tk.W )
        self.addEntryBox( 0, 0, frame4, "ファイル名: ", user_input.save_file, "file_name", 60, getcwd()+"\\out.txt" )
        self.addEntryBox( 0, 1, frame4, "区切り文字: ", user_input.save_file, "delimiter", 3, "," )

        self.outputSpeakerCount()


    def addCheckBoxes( self, c, r, frame, frame_title, dictionary, widget_list ):
        '''for each entry in the list, add a check box to the frame, and
        record the interface variables in the dictionary'''
        pad_x = 10; pad_y = 5
        host = ttk.LabelFrame( frame, text=frame_title)
        host.grid( column=c, row=r,  padx=pad_x, pady=pad_y, sticky=tk.W )
        c = 0
        r = 0
        for widget in widget_list:
            #a widget is tuplet consisting of a code form and a Japanese text form, ex., ("F", "女性")
            var_key = widget[0] + "_tkVar"
            widget_key = widget[0] + "_widget"
            dictionary[var_key] = tk.IntVar()
            dictionary[widget_key] = tk.Checkbutton( host, text=widget[1], variable=dictionary[var_key], command=lambda: self.outputSpeakerCount() )
            dictionary[widget_key].select()
            dictionary[widget_key].grid( column=c, row=r, ipadx=10, ipady=3, sticky="W" )
            c += 1
            if c == 3: c = 0; r += 1 

    def addRadioButtons( self, c, r, frame, frame_title, dictionary, widget_list, interface_name ):
        '''for each entry in the list, add a radio button to the frame
        there is only one tk variable recorded in the dictionary for radio buttons
        but there is still one widget variable per button recorded in the dictionary'''
        pad_x = 10; pad_y = 5
        host = ttk.LabelFrame( frame, text=frame_title)
        host.grid( column=c, row=r,  padx=pad_x, pady=pad_y, sticky=tk.W )
        #set up the interface variable
        var_key = interface_name + "_tkVar"
        dictionary[var_key] = tk.StringVar()
        i = 0
        for widget in widget_list:
            #a widget is tuplet consisting of a code form and a Japanese text form, ex., ("F", "女性")
            widget_key = widget[0] + "_widget"
            dictionary[widget_key] = tk.Radiobutton( host, text=widget[1], variable=dictionary[var_key], value=widget[0], command=lambda: self.outputSpeakerCount() )
            dictionary[widget_key].grid( column=i, row=0, ipadx=10, ipady=3 )
            i += 1
        dictionary[widget[0] + "_widget"].select()

    def addEntryBox( self, c, r, frame, text_in_front, dictionary, interface_name, size, start_value ):
        '''add a text entry box preceeded by the text_in_front
        fill the text box with the start value'''
        label = ttk.Label(frame, text=text_in_front)
        label.grid(column=c, row=r, ipadx=0, ipady=3, sticky='E')
        var_key = interface_name + "_tkVar"
        dictionary[var_key] = tk.StringVar()
        dictionary[var_key].set( start_value )
        widget_key = interface_name + "_widget"
        dictionary[widget_key] = ttk.Entry(frame, width=size, textvariable=dictionary[var_key])
        dictionary[widget_key].grid(column=c+1, row=r, ipadx=10, ipady=3, sticky='W')

    def addOutputBox( self, frame ):
        scrolW = 39
        scrolH = 6
        self.output_box = sctxt.ScrolledText( frame, width=scrolW, height=scrolH, wrap=tk.CHAR )
        self.output_box.grid( column=0, ipadx=10, ipady=3, sticky='W' )

    def addComboBox( self, c, r, frame, text_in_front, dictionary, interface_name, size, start_list ):
        '''add a drop down combo box preceeded by the text_in_front
        fill the combo box with the start list'''
        label = ttk.Label(frame, text=text_in_front)
        label.grid(column=c, row=r, ipadx=0, ipady=3)
        var_key = interface_name + "_tkVar"
        dictionary[var_key] = tk.StringVar()
        widget_key = interface_name + "_widget"
        dictionary[widget_key] = ttk.Combobox(frame, width=size, textvariable=dictionary[var_key], values=start_list, state='readonly')
        dictionary[widget_key].current( 0 )
        dictionary[widget_key].grid(column=c+1, row=r, ipadx=10, ipady=3, sticky='W')

    def addSpinBox( self, c, r, frame, text_in_front, dictionary, interface_name, size, start, end ):
        '''add a spin box preceeded by the text_in_front'''
        label = ttk.Label(frame, text=text_in_front)
        label.grid(column=c, row=r, ipadx=0, ipady=3)
        var_key = interface_name + "_tkVar"
        dictionary[var_key] = tk.StringVar()
        dictionary[var_key].set( int( (end-start)/2)+1 )
        widget_key = interface_name + "_widget"
        dictionary[widget_key] = tk.Spinbox(frame, width=size, from_=start, to=end, borderwidth=2, textvariable=dictionary[var_key])
        dictionary[widget_key].grid(column=c+1, row=r, ipadx=10, ipady=3, sticky='W')

    def searchExpression( self ):
        self.output_box.delete(1.0, tk.END)
        self.output_box.insert(tk.END, "\nしばらくお待ちください。\n")
        try:
            selected_speakers = user_input.getLimitedSpeakerList()
            if len( selected_speakers ) == 0: raise ValueError("インタビューファイルが選択されていません。")
            voice = user_input.voice["voice_tkVar"].get()
            search_expression = user_input.search_expression["expression_tkVar"].get()
            search_expression_length = len( search_expression )
            if search_expression_length == 0: raise ValueError("検索表現がありません。")
            front_padding_length = int( user_input.search_expression["front_tkVar"].get() )
            back_padding_length = int( user_input.search_expression["back_tkVar"].get() )
            save_file =  user_input.save_file["file_name_tkVar"].get()
            delimiter = user_input.save_file["delimiter_tkVar"].get()
            fh = open( save_file, "w", encoding='utf-8' )
        except IOError:
            self.output_box.insert(tk.END, "\n出力ファイルを開けることが出来ません。\n行動を中止します。" )
        except ValueError as e:
            self.output_box.insert(tk.END, "\n{}\n行動を中止します。" .format(e.args[0]) )
        else:
            fh.write( delimiter.join( ["コーパス", "番号", "年齢", "性別", "前", "表現", "後ろ\n"] ) )
            count = 0
            for s in selected_speakers:
                speaker = speaker_list.getSpeaker( s )
                corpus = self.convert_to_string[speaker.corpus]
                number = speaker.number
                age = self.convert_to_string[speaker.age]
                sex = self.convert_to_string[speaker.sex]
                interview = speaker.getInterview( voice, speechOnly = 'True' ) #gets interview as a string
                interview_length = len( interview )
                for i in range( 1, interview_length-search_expression_length-1 ):
                    #use the atLeast and atMost functions to make sure that we do not go beyond the edges of the interview
                    window_start = i
                    window_end = self.atMost( i + search_expression_length, interview_length )
                    front_padding_end = window_start
                    front_padding_start = self.atLeast( front_padding_end - front_padding_length, 0 )
                    back_padding_start = self.atMost( window_end, interview_length )
                    back_padding_end = self.atMost( back_padding_start + back_padding_length, interview_length )
                    if interview[ window_start : window_end ] == search_expression:
                        output = delimiter.join( [corpus, number, age, sex,
                                                 interview[ front_padding_start : front_padding_end ], 
                                                 interview[ window_start : window_end ], 
                                                 interview[ back_padding_start : back_padding_end ] + "\n"] )
                        fh.write( output )
                        count += 1
            fh.close()
            self.output_box.insert(tk.END, "\n検索した表現を{}件出力しました。\n".format(count) )
                        
    def searchMorpheme( self ):
        self.output_box.delete(1.0, tk.END)
        self.output_box.insert(tk.END, "\nしばらくお待ちください。\n")
        try:
            selected_speakers = user_input.getLimitedSpeakerList()
            if len( selected_speakers ) == 0: raise ValueError("インタビューファイルが選択されていません。")
            selected_voice = user_input.voice["voice_tkVar"].get()
            save_file =  user_input.save_file["file_name_tkVar"].get()
            fh = open( save_file, "w", encoding='utf-8' )
            delimiter = user_input.save_file["delimiter_tkVar"].get()

            #make six lists containing the contents of the 変異形 and their pos fields
            #only add non-empty items
            target_list1 = []; target_list2 = []; target_list3 = []
            target_pos_list1 = []; target_pos_list2 = []; target_pos_list3 = []
            for i in range (1, 4):
                m_key = "morpheme1" + str(i) + "_tkVar"
                p_key = "morpheme1" + str(i) + "_pos_tkVar"
                input_box_contents = user_input.search_morpheme[ m_key ].get()
                input_box_pos = user_input.search_morpheme[ p_key ].get()
                if input_box_contents != "": target_list1.append( input_box_contents ) #only add if not empty
                if input_box_pos != "未定": target_pos_list1.append( input_box_pos )
            for i in range (1, 4):
                m_key = "morpheme2" + str(i) + "_tkVar"
                p_key = "morpheme2" + str(i) + "_pos_tkVar"
                input_box_contents = user_input.search_morpheme[ m_key ].get()
                input_box_pos = user_input.search_morpheme[ p_key ].get()
                if input_box_contents != "": target_list2.append( input_box_contents ) #only add if not empty
                if input_box_pos != "未定": target_pos_list2.append( input_box_pos )
            for i in range (1, 4):
                m_key = "morpheme3" + str(i) + "_tkVar"
                p_key = "morpheme3" + str(i) + "_pos_tkVar"
                input_box_contents = user_input.search_morpheme[ m_key ].get()
                input_box_pos = user_input.search_morpheme[ p_key ].get()
                if input_box_contents != "": target_list3.append( input_box_contents ) #only add if not empty
                if input_box_pos != "未定": target_pos_list3.append( input_box_pos )
            if len( target_list1 ) + len( target_pos_list1 ) + len( target_list2 ) + len( target_pos_list2 ) + len( target_list3 ) + len( target_pos_list3 ) == 0:
                raise ValueError("検索形態素情報がありません。")

        except IOError:
            self.output_box.insert(tk.END, "\n出力ファイルを開けることが出来ません。\n行動を中止します。" )
        except ValueError as e:
            self.output_box.insert(tk.END, "\n{}\n行動を中止します。" .format(e.args[0]) )
        else:
            fh.write( delimiter.join( ["コーパス", "番号", "年齢", "性別", "発話者", "一位の形態素", "一位の品詞", "二位の形態素", "二位の品詞","三位の形態素", "三位の品詞\n"] ) )
            count = 0
            for s in selected_speakers:
                speaker = speaker_list.getSpeaker( s )
                corpus = self.convert_to_string[speaker.corpus]
                number = speaker.number
                age = self.convert_to_string[speaker.age]
                sex = self.convert_to_string[speaker.sex]
                interview = speaker.getInterview( selected_voice, speechOnly = False ) #gets interview as a list
                #set up the first data
                first_morpheme = [ "", "", "", "", "", "", "", "", "" ]
                second_morpheme = interview.pop()
                third_morpheme = interview.pop()
                for item in interview:
                    #shift all of the morphemes by one position
                    first_morpheme = second_morpheme
                    second_morpheme = third_morpheme
                    third_morpheme = item
                    #check to see if the morphemes match the corresponding search list or the list is empty
                    #Note: an empty list equates to False, so not empty_list equates to True
                    isMorpheme1Ok = False; isMorpheme2Ok = False; isMorpheme3Ok = False
                    isMorpheme1posOk = False; isMorpheme2posOk = False; isMorpheme3posOk = False
                    if ( (first_morpheme[0] in target_list1) or (not target_list1) ):
                        isMorpheme1Ok = True
                    if ( (second_morpheme[0] in target_list2) or (not target_list2) ):
                        isMorpheme2Ok = True
                    if ( (third_morpheme[0] in target_list3) or (not target_list3) ):
                        isMorpheme3Ok = True
                    if ( (first_morpheme[2] in target_pos_list1) or (not target_pos_list1) ):
                        isMorpheme1posOk = True
                    if ( (second_morpheme[2] in target_pos_list2) or (not target_pos_list2) ):
                        isMorpheme2posOk = True
                    if ( (third_morpheme[2] in target_pos_list3) or (not target_pos_list3) ):
                        isMorpheme3posOk = True
                    #If all six isOk are True then extract the morpheme
                    if isMorpheme1Ok and isMorpheme2Ok and isMorpheme3Ok and isMorpheme1posOk and isMorpheme2posOk and isMorpheme3posOk:
                        output = delimiter.join( [corpus, number, age, sex, first_morpheme[1], first_morpheme[0], first_morpheme[2], 
                                                  second_morpheme[0], second_morpheme[2],
                                                  third_morpheme[0], third_morpheme[2] + "\n" ] )
                        fh.write( output )
                        count += 1
            self.output_box.insert(tk.END, "\n検索した表現を{}件出力しました。\n".format(count) )
            fh.close()
 
    def outputSpeakerCount( self ):
        selected_speakers = user_input.getLimitedSpeakerList()
        selected_speaker_count = len( selected_speakers ) 
        self.output_box.delete(1.0, tk.END)
        self.output_box.insert(tk.END, "\nインタビューファイルが{}件選択されています。\n".format( selected_speaker_count ) )

    def start( self ):
        self.win.mainloop()

    def createSearchExpressionThread( self ):
        t = Thread( target = self.searchExpression )
        t.setDaemon(True)
        t.start()

    def createSearchMorphemeThread( self ):
        t = Thread( target = self.searchMorpheme )
        t.setDaemon(True)
        t.start()

###INITIALIZATION###
speaker_list = Corpus()
files = listdir( FILE_DIR )
for file in files:
    found = FILE_NAME_PATTERN.search( file )
    #see note on re groups above
    code = found.group(1)
    number = found.group(2)
    gender = found.group(3)
    age = found.group(4)    
    new_speaker = Speaker( code, number, gender, age )
    key = str( code + number + gender + age )
    speaker_list.addSpeaker( new_speaker,  key)

###Start GUI###
gui_interface = Interface()
user_input = InputTracker()
gui_interface.build()
gui_interface.start()
