import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext as sctxt
from tkinter import filedialog
import kana_converter as kc
import file_handler2 as fh
import sys,os

##################################################
# ます	助動詞, *, *, *, 特殊マス, 基本形, ます, マス, マス
#   0             1      2  3 4        5            6          7        8      9      
##################################################

###################
# GLOBAL VARIABLES
###################

POS_LIST = [ ("ippn", "一般名詞"), ("koyu", "一般固有名詞"), ("chik", "地域"), ("sshk", "組織"), ("jnme", "人名"), ("kyds", "形容動詞"), ("shsz", "サ変接続"), ("knsh", "感動詞"), ("fksh","副詞"), ("fllr", "フィラー"), ("eigo", "英語") ]
POS_LENGTH_LIST = [10, 2, 8, 1, 1, 1, 1, 2, 8, 8, 8]

###################
# Interface objects
###################

class Interface():
    '''This object is the actual GUI interface. Use the build method to create the interface.
    This object tracks the status and contents of all of the labels, radio buttons, check boxes and entry boxes.
    This is done inside a dictionary called interface_dic.
    The key determines which part of the interface is accessed.
    Use the .set() and .get() methods to set and get the contents of the buttons, fields, etc.
    Example:
    self.interface_dic["pos_tkVar"].get() returns the status of the radio boxes.
    List of keys:
    "target_tkVar": the contents of the target window
    "context_tkVar": the contents of the context window
    "pos_tkVar": the pos radio buttons
        >> Note: the pos radio buttons are linked to the following codes:
        >>ippn = 一般名詞; koyu = 一般固有名詞; chik = 地域; sshk = 組織, jnme = 人名; kyds =形容動詞; shsz = サ変接続; knsh = 感動詞; fksh = 副詞; fllr = フィラー; eigo = 英語
    "..._tkVar"; where ... is one of 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10: the edit by hand entry boxes
    "can_tkVar": the candidate radio buttons

    self.interface_dic[ "file" ] returns the selected file once it has been selected
    '''    

    def __init__( self, speaker_file_object, clustered_homs ):
        self.win = tk.Tk()
        self.win.title("Homonym annotator" )
        self.win.resizable(0, 0)
        self.interface_dic = {}
        self.clustered_homs=clustered_homs
        self.clustered_homs_bases=[CH.cluster_on for CH in self.clustered_homs]
        self.fixer = fh.HomProblemFixer(speaker_file_object)
        self.candidates_list = []

    def build( self ):
        #frame1: the problematic entry and its line number
     #   self.frame_tgt = ttk.LabelFrame(self.win, text="データ", borderwidth=5 )
      #  self.frame_tgt.grid(column=0, row=0, padx=5, pady=5, sticky=tk.W )
#        self.interface_dic["target_tkVar"] = tk.StringVar()
       # ttk.Label(self.frame_tgt, text="行番号").grid(column=0, row=0)

        #frame2: context
        self.frame_cxt = ttk.LabelFrame(self.win, text="コンテクスト", borderwidth=5 )
        self.frame_cxt.grid(column=0, row=1, padx=5, pady=5, sticky=tk.W )

        ttk.Label(self.frame_cxt, textvariable = '' ).grid(column=0, row=0)
        
        #frame3: candidates radio buttons
        self.frame_correct = ttk.LabelFrame(self.win, text="候補の文字", borderwidth=5 )
        self.frame_correct.grid(column=0, row=2, padx=5, pady=5, sticky=tk.W )

        #frame4: edit by hand, contains frames 4a and 4b
        self.frame_manual = ttk.LabelFrame(self.win, text="手で修正する", borderwidth=5 )
        self.frame_manual.grid(column=0, row=3, padx=3, pady=3, sticky=tk.W )
#        self.addRadioButtons( 0, 1, self.frame4, "品詞", self.interface_dic, POS_LIST, "pos", "horizontal" )
        #frame5: skip
        self.frame_skip = ttk.LabelFrame(self.win, text="修正せずに飛ばす", borderwidth=5 )
 #       self.frame_skip.grid(column=0, row=4, padx=3, pady=3, sticky=tk.W )
        skip_button1 = ttk.Button(self.frame_skip, text="ファイルに記録して中断", command = self.skipWithRecord )
        skip_button1.grid(column=0, row=0)
  #      skip_button2 = ttk.Button(self.frame_skip, text="記録せずに飛ばす", command = self.skipWithoutRecord )
   #     skip_button2.grid(column=1, row=0)
        
    def populate_widgets(self):
        Bases=[list(Dict.values()) for Dict in self.clustered_homs_bases]
        all_in_str= lambda Str,Lst: all(El in Str for El in Lst)
        HitBase=self.fixer.sfo.getProblemRecord(lambda Str: next( (Base for Base in Bases if all_in_str(Str,Base)), None))
        probRec=self.fixer.sfo.problem_record

#        self.frame_tgt['text']=probRec.record
#        self.frame1['text']='ライン番号: ' +         self.interface_dic["target_tkVar"]

        context = self.fixer.sfo.getContextAsString()
        self.frame_cxt['text']= context 
#        self.frame2['text']= self.interface_dic["context_tkVar"] 
        #self.candidates_list = self.sfo.getCandidates( self.sfo.problem_record.record[0] ) #list is empty if no candidates found
        #self.addRadioButtons( 0, 0, frame_correct, "", self.interface_dic, self.candidates_list, "can", "vertical")
        CH=next(CH for CH in self.clustered_homs if list(CH.cluster_on.values())==HitBase)
        self.candidates_list = self.fixer.getCandidates( probRec,CH ) #list is empty if no candidates found
        WdOrths=[Wd.orth for Wd in self.candidates_list]
        for Cntr,WdOrth in enumerate(WdOrths):
            ttk.Label(self.frame_correct,text=WdOrth).grid(row=Cntr,column=0)
            ttk.Entry(self.frame_correct,width=2).grid(row=Cntr,column=1)
#        self.addRadioButtons( 0, 0, self.frame_correct, WdOrths, "can", "vertical")
        ttk.Button(self.frame_correct, text="確定", command = self.editByCandidate ).grid(column=1, row=2,sticky='es')
        
        
                #frame4a = ttk.LabelFrame(frame4, text="", borderwidth=5 )
        #frame4a.grid(column=0, row=0, padx=3, pady=3, sticky=tk.W )
        #edit_hand_start_button = ttk.Button(frame4a, text="修正", command = self.editByHand )
        #edit_hand_start_button.grid(column=12, row=0)
        #for i in range(0,10):
        #    self.addEntryBox( i, 0, frame4a, "", self.interface_dic, str( i ), POS_LENGTH_LIST[i], "" )
        #self.interface_dic["ippn_widget"].select()
        #self.changePOS()
    def addRadioButtons( self, c, r, frame, items, interface_name, direction ):
        '''for each entry in the list, add a radio button to the frame
        there is only one tk variable recorded in the dictionary for radio buttons
        but there is still one widget variable per button recorded in the dictionary'''
        pad_x = 5; pad_y = 5
        host = ttk.LabelFrame( frame )
        host.grid( column=c, row=r,  padx=pad_x, pady=pad_y, sticky=tk.W )
        #set up the interface variable
 #       var_key = interface_name + "_tkVar"
  #      dictionary[var_key] = tk.StringVar()
        #i = 0
        for Ind,item in enumerate(items):
            #a widget is tuplet consisting of a code form and a Japanese text form: ("F", "女性")
            #in the case of a candidate, then the tuple contains a digit and an record ("1", "行き\t動詞, ...")
           # widget_key = widget[0] + "_widget"
            tk.Radiobutton( frame, text=item,value=False).grid(sticky='nw')# variable=dictionary[var_key], value=widget[0], command=lam )
            #if direction == "horizontal": dictionary[widget_key].grid( column=i, row=0, ipadx=10, ipady=3, sticky=tk.W )
            #elif direction == "vertical": dictionary[widget_key].grid( column=0, row=i, ipadx=10, ipady=3, sticky=tk.W )
            #dictionary[widget_key].select()
            
        
        
    def addEntryBox( self, c, r, frame, text_in_front, dictionary, interface_name, size, start_value ):
        '''add a text entry box preceeded by the text_in_front
        fill the text box with the start value'''
        label = ttk.Label(frame, text=text_in_front)
        label.grid(column=c, row=r, ipadx=0, ipady=3, sticky='E')
        var_key = interface_name + "_tkVar"
        dictionary[var_key] = tk.StringVar()
        dictionary[var_key].set( start_value )
        widget_key = interface_name + "_widget"
        dictionary[widget_key] = ttk.Entry(frame, width=size, textvariable=dictionary[var_key], justify='center')
        dictionary[widget_key].grid(column=c+1, row=r, ipadx=10, ipady=3, sticky='W')
        
    def changePOS( self ):
        selected_pos = self.interface_dic["pos_tkVar"].get()
        item = self.sfo.problem_record.record[0]
        kana = kc.toKana( item )
        if selected_pos == "ippn": new_list = [item, "名詞" , "一般" , "*", "*", "*", "*", item, kana, kana]
        elif selected_pos == "jnme": new_list = [item, "名詞", "固有名詞", "人名", "名", "*", "*", item, kana, kana]
        elif selected_pos == "koyu": new_list = [item, "名詞", "固有名詞", "一般", "*", "*", "*", item, kana, kana]
        elif selected_pos == "chik": new_list = [item, "名詞", "固有名詞", "地域", "一般", "*", "*", item, kana, kana]
        elif selected_pos == "sshk": new_list = [item, "名詞", "固有名詞", "組織", "*", "*", "*", item, kana, kana]
        elif selected_pos == "kyds": new_list = [item, "名詞" , "形容動詞語幹" , "*", "*", "*", "*", item, kana, kana]
        elif selected_pos == "shsz": new_list = [item, "名詞" , "サ変接続" , "*", "*", "*", "*", item, kana, kana]
        elif selected_pos == "fksh": new_list = [item, "副詞" , "一般" , "*", "*", "*", "*", item, kana, kana]
        elif selected_pos == "knsh": new_list = [item, "感動詞" , "*" , "*", "*", "*", "*", item, kana, kana]
        elif selected_pos == "fllr": new_list = [item, "フィラー" , "*" , "*", "*", "*", "*", item, kana, kana]
        elif selected_pos == "eigo": new_list = [item, "英語" , "*" , "*", "*", "*", "*", "*", "*", "*"]
        else: new_list = [] #this will crash with an index error
        for i in range (0, 10): #fill in the eidt by hand entry boxes with the pos information for the chosen radio button
            self.interface_dic[ str( i ) + "_tkVar"].set( new_list[i] )

    def editByHand( self ):
        selected_pos = self.interface_dic["pos_tkVar"].get()
        temp = ""
        #build up a string of parts from the edit by hand entry boxes
        for i in range (0, 9):
            temp += self.interface_dic[ str( i ) + "_tkVar"].get() + ","
        temp += self.interface_dic[ "9_tkVar"].get() + "\n"
        temp_record = fh.Record( temp )
        temp_record.speaker = self.sfo.problem_record.speaker
        self.sfo.fixProblemRecord( temp_record, selected_pos )
        self.quit()

    def editByCandidate( self ):
        i = int( self.interface_dic["can_tkVar"].get() ) #get the number of the selected candidate
        temp = self.candidates_list[i] #this is a tuple
        record_part_only = temp[1] #this is the record portion of the tuple
        temp_record = fh.Record( record_part_only )
        temp_record.speaker = self.sfo.problem_record.speaker
        self.sfo.fixProblemRecord( temp_record, pos = "" ) #only pass pos if edited by hand
        self.quit()

    def skipWithRecord( self ):
        self.sfo.skipRecord( write_to_skip_file = True )
        self.quit()

    def skipWithoutRecord( self ):
        self.sfo.skipRecord( write_to_skip_file = False )
        self.quit()


        

    def start( self ):
        self.populate_widgets()

        self.win.focus_force()
        self.win.mainloop()

    def quit( self ):
        self.win.quit()
        self.win.destroy()

def fileOpener():
    options = {}
#    options['filetypes'] = [('all files', '.*'), ('mecab files', '.mecab')]
    options['initialdir'] = os.path.join(os.getcwd(),"in")
    root = tk.Tk()
    root.withdraw()
    file_name = tk.filedialog.askopenfilename( **options )
    root.quit()
    root.destroy()
    return file_name
