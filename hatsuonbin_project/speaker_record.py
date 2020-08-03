class Record:
    '''This object is a list with a string representation.
    It receives a mecab file line as input.
    The file line must have a speaker tag
    The string version of this object includes the tab, but it does not include the speaker tag
    Properties:
        self.record: if speaker = "s", then a list of the record parts; otherwise a bunch of periods
        self.speaker: the speaker tag
    Methods:
        getFullRecord: The method self.getFullRecord() returns the record as a string including the speaker tag (if there there is one) 
    '''
    def __init__( self, record = ".	.,.,.,.,.,.,.,.,.,x\n" ):
        speaker_tags = ("s", "i", "s2", "i2", "x")
        #Change EOS records to match the format of other records
        if record == "EOS\n": record = "EOS	.,.,.,.,.,.,.,.,.,x"
        record = record.strip()
        temp = record.replace("\t", ",")
        temp = temp.split( "," )
        if temp[-1] in speaker_tags:
            self.speaker = temp.pop(-1) #the pop(-1) method removes and returns the last element from the record list
        else:
            raise ValueError("Unidentifiable speaker tag: {}.\n".format( record ) )        
        #the length of temp should be either 10
        number_record_parts = len( temp )
        if number_record_parts != 10:
            raise ValueError("Wrong number of record parts: {}.\nRecord: {}.".format( number_record_parts, record ) )
        if self.speaker == "s":
            self.record = temp
        else:
            self.record = [".",".",".",".",".",".",".",".",".","."]

    def __repr__( self ):
        temp = ",".join( self.record )
        return temp.replace( ",", "\t", 1 )

    def getFullRecord( self ):
        '''Returns a Record object as a single string matching the format of a mecab file line
          If the Record contains an EOS record, then return EOS\n 
          '''
        #handle EOS records
        if self.record[0] == "EOS\n":
            return "EOS\n"
        #add the speaker tag, if there is one
        if self.speaker != "False":
            #include the speaker tag in the string
            return self.record[0] + "\t" + ",".join( self.record[1:11] ) + "," + self.speaker + "\n"
        else:
            #do not add a speaker tag
            return self.record[0] + "\t" + ",".join( self.record[1:11] ) + "\n"
