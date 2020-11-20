import os

SUP_FILE = os.path.dirname(__file__) + "/dic_files/west_supplement.csv"
NOUN_FILE = os.path.dirname(__file__) + "/dic_files/west_nouns.csv"
DIC_DIR = os.path.dirname(__file__) + "/dic_files/"
STRIPPED_DIC_DIR = os.path.dirname(__file__) + "/stripped_dic_files/"

class CorpusDictionaries:
    '''This class contains the contents of all of the corpus dictionaries. It is used to compare a mecab file against the dictionaries
    in order to find records that are not in the dictionaries.
    Properties:
      self.dic: All of the contents of the dictionary files are stored in this dictionary; each dictionary entry becomes the key, with True as the value
    Methods:
      self.getCandidates( item ): Returns a list. Each list item is a dictionary entry that matches item. For example, if item = "いける" then get
        all of the dictionary entries for いける.
      self.addNewItem: First check to see if the item is in the dictionary self.dic. If it is, then do nothing. If it is not, then write it to a file, and and add it to self.dic'''
    def __init__( self, strip_dictionaries = False ):
        print("strip_dictionaries", strip_dictionaries)
        self.dic = {}
        if strip_dictionaries:
            print( "Striping the dictionaries...\n")
            files = os.listdir( DIC_DIR )
            for file in files:
                file_parts = file.split( "." )
                #Some files do not have an extension. Therefore file_parts[1] is null.
                #Accessing a null element of a string raises an IndexError.
                #Catch it and go on.
                try:
                    if file_parts[1] == "csv" in file:
                        out_file = file_parts[0]+"_stripped.csv"
                        print( out_file )
                        in_fh = open( DIC_DIR + file, "r", encoding = "utf-8" )
                        out_fh = open( STRIPPED_DIC_DIR + out_file, "w", encoding = "utf-8" )
                        line_count = 0
                        while True:
                            record = in_fh.readline()
                            line_count += 1
                            if record == "": break
                            #split up the record on the comma
                            #then rebuild th record without the number elements
                            record_parts = record.split( "," )
                            number_of_items = len( record_parts )
                            if number_of_items != 13: raise ValueError("Only {} parts on line {} of {}.".format( number_of_items, line_count, out_file ) )
                            new_record = record_parts[0] + "\t" + record_parts[4] + "," + record_parts[5] + "," + record_parts[6] + "," + record_parts[7] + "," + record_parts[8] + "," + record_parts[9] + "," + record_parts[10] + "," + record_parts[11] + "," + record_parts[12] 
                            out_fh.write( new_record )   
                        in_fh.close()
                        out_fh.close()
                except IndexError:
                    print ( "Skipping {}".format(file_parts[0]) )

        print( "\n\nReading in the dictionary files...\n" )
        dic_files = os.listdir( STRIPPED_DIC_DIR )
        for dic_file in dic_files:
            print( dic_file )
            dic_fh = open( STRIPPED_DIC_DIR + dic_file, "r", encoding = "utf-8" )
            while True:
                dic_record = dic_fh.readline()
                if dic_record == "": break
                self.dic[ dic_record ] = True #each line of data becomes a key, with "True" as the look up element

    def getCandidates( self, item ):
        temp = []
        for key in self.dic.keys():
            key_parts = key.split( "\t" )
            if item == key_parts[0]:
                temp.append( key )
        return temp

    def addNewItem( self, item, pos ):
        #ippn = 一般名詞; koyu = 一般固有名詞; chik = 地域; sshk = 組織, jnme = 人名; knsh = 感動詞; fksh = 副詞; fllr = フィラー; kyds = 形容動詞; shsz = サ変接続
        #if pos is one of [ippn, koyu, chik, sshk, jnme] then add to NOUN_FILE
        #if pos is one of [knsh, fksh, fllr, kyds, shsz] then add to SUP_FILE
        #if pos is [eigo] then do not add to the dictionaries
        #if pos empty then the source of the item is the candidates radio buttons
        #all of these items already exist in the dictionaries, so just return
        if self.dic.get( item, False ):
            #returns True if the item is already in the dictionary
            #in that case, do nothing
            return
        if pos in ["ippn", "koyu", "chik", "sshk", "jnme"]: file = NOUN_FILE
        elif pos in ["knsh", "fksh", "fllr", "kyds", "shsz"]: file = SUP_FILE
        else: return
        self.dic[ item ] = True
        item = item.replace("\t", ",0,0,0," )
        fh = open( file, "a", encoding = "utf-8" ); fh.write( item ); fh.close
        return

        
