from shutil import copyfile
import os
import re
import dictionary_handler as dh
import asyncio as a

class Record:
    '''This object is a list with a string representation.
    It receives a mecab file line as input. The file line may or may not have a speaker tag.
    The attribute self.record contains the record as a list without the speaker tag.
    If there was a speaker tag, then self.speaker contains it. Otherwise, self.speaker contains False.
    The string version of this object includes the tab, but it does not include the speaker tag.
    Two Record() objects are equal if all parts but the speaker tags are equal.
    The method self.getFullRecord() returns a string that contains the speaker tag (if there there is one) 
    '''
    def __init__( self, record ):
        tags = ("s,", "i,", "s2,", "i2,", ".,")
        #count the number of commas; it must be 8 (subtract one befor checking if there is a speaker tag)
        comma_count = record.count( "," )
        if any(tag in record for tag in tags): #if there is any tag in temp, then return True
            comma_count -= 1
        if comma_count != 8 and comma_count != 6:
            print( "Wrong number of commas: {}.".format( comma_count ) )
            print( "Line:", record ) 
        temp = record.replace("\t", ",")
        temp = temp.split( "," )
        try:
            if temp[1] in tags:
                self.speaker = temp.pop(1) #the pop method removes and returns element 1 from the record list
            else:
               self.speaker = False
            self.record = temp
        except:
            print( "Index Error with record: ", record )


    def __repr__( self ):
        temp = ",".join( self.record )
        return temp.replace( ",", "\t", 1 )

    def __eq__( self, other ):
        if self.record == other.record: return True
        else: return False

    def getFullRecord( self ):
        if self.speaker:
            #make the front half of the string, up to the speaker tag
            temp = self.record[0] + "\t" + self.speaker + ","
            #append the remainder of the the pos information and returnt he string
            return temp + ",".join( self.record[1:10] )
        else:
            #as above but do not add a speaker tag
            temp = self.record[0] + "\t"
            return temp + ",".join( self.record[1:10] )
        
class SpeakerFile:
    '''This object handles a speaker file.
    Properties:
        file: the name of the file, incuding directory and the extention
        skipped_file: a file create to record the skipped records; name includes directory and extenstion
        temp_file: a file used when repairing a problem record
        log_file: a record of all repair operations
        problem_record: a record object that contains the parts of the problem record
        line: the file line number of the problem record
        context: a queue containing the 25 characters immediately before and after the problem record
        skipped_record_line_numbers: a dictionary containing a list of skipped record line numbers; data value is True of each item
          so that self.skipped_record_line_numbers.get( line, False ) returns True if the record has previously been skipped
    Methods:
        getProblemRecord: goes through the file until it finds a problem record, skipping over any 
            previously skipped records, then sets problem_record, and line, and context
        fixProblemRecord: adds the fix to the dictionaries, goes through the file and  fixes all occurances of problem record with
            the fix; returns the number of fixes made as an interger
        skipRecord: writes the problem_record to the skipped_file
        addToContext: add a morpheme to the context queue, while maintaining the queue size
        getContextAsString: return the contents of the context queue as a string
        getFileLine: reads in a record, breaks it up into parts and returns it as a Record() object with the record.speaker set to the speaker tag
        getCandidates: returns a list of tuples containing enumerated records of possible candidates for the fix; [ ( "0", "record") , ... ]
    '''
    #class variables shared by all instances of this class
    corpus_dic = dh.CorpusDictionaries( strip_dictionaries = True )
    
    def __init__( self, file ):
        self.file = file
        file_parts = file.split( '.' )
        self.skipped_file = file_parts[0] + "_skipped.txt"
        self.log_file = file_parts[0] + "_log.txt"
        #empty out the contents of the skipped file by opening and closing it
        fh_temp = open( self.skipped_file, "w", encoding = "utf-8" )
        fh_temp.close()
        #empty out the contents of the log file by opening and closing it
        fh_temp = open( self.log_file, "w", encoding = "utf-8" )
        fh_temp.close()
        self.skipped_record_line_numbers = {}
        self.temp_file =  file_parts[0] + "_temp.txt"
        self.problem_record = ""
        self.line = 0
        self.context = a.Queue()

    def addToContext( self, item ):
        if self.context.qsize() > 50: #queue is full, so remove one item first
            temp = self.context.get_nowait()
        self.context.put_nowait( item )

    def getContextAsString( self ):
        temp = ""
        while self.context.qsize() > 1:
            temp += self.context.get_nowait()
        return temp

    def getFileLine (self, file_handle ):
        '''Read in a record, split into parts, extract the speaker tag
        Set the parts list as a record object. Set the speaker tag.
        Return the record object.'''
        file_line = file_handle.readline()
        #Skip over EOS
        if file_line == "EOS\n": file_line = file_handle.readline() #This will crash if there are two EOS in a row
        if  file_line == "":
            file_handle.close()
            raise IOError
        #replace the tab with a comma and split up into parts
        temp_record = Record( file_line )
        return temp_record

    def getProblemRecord( self ):
        in_fh = open( self.file, "r", encoding = "utf-8" )
        self.line = 0
        try:
            while True:
                temp_record = self.getFileLine( in_fh )
                self.line += 1
                if re.search("^\d+\t", str(temp_record) ):
                    #if one or more digits followed by a tab, then add record to context, and continue to next record
                    self.addToContext( temp_record.record[0] )
                    next
                elif "英語," in str(temp_record):
                    #skip over the lines that have already been tagged as English
                    self.addToContext( temp_record.record[0] )
                    next                    
                elif self.skipped_record_line_numbers.get( self.line, False ):
                    #we have already skipped this record once, so just add it to the context and continue to next record
                    self.addToContext( temp_record.record[0] )
                    next
                elif SpeakerFile.corpus_dic.dic.get( str(temp_record), False ):
                    #if already in the dictionary then add record to context, and continue to next record
                    self.addToContext( temp_record.record[0] )
                    next
                else:
                    #we found something not in the dictionaries
                    self.problem_record = temp_record
                    self.addToContext( " ### " )
                    self.addToContext( temp_record.record[0] )
                    self.addToContext( " ### " )
                    try:
                        for i in range(0, 25):
                            temp_record = self.getFileLine( in_fh )
                            self.addToContext( temp_record.record[0] )
                        in_fh.close()
                        return
                    except IOError:                          
                        in_fh.close()
                        return
        except IOError:
            in_fh.close()
            raise IOError
                
    def fixProblemRecord( self , fix_record, pos ):
        '''Receives a Record() object as input.
        First add the fix to the dictionaries.
        Then replace every occurance of probem_record with fix_record in the mecab file.'''
        self.corpus_dic.addNewItem( str( fix_record ), pos )
        #English records are not added to the dictionaries
        #English records are added to the list of records to skip over
        if pos == "eigo": self.skipped_record_line_numbers[ self.line ] = True        
        in_fh = open( self.file, "r", encoding = "utf-8" )
        temp_fh = open( self.temp_file, "w", encoding = "utf-8" )
        while True: #continue until EOF
            temp = in_fh.readline()
            if temp == "EOS\n": temp = in_fh.readline() #This will crash if there are two EOS in a row
            if temp == "": break
            #go through the file one line at a time while looking for the broken record
            #write out each line to the temp file
            record = Record( temp )
            if record == self.problem_record: #located the problem record
                temp_fh.write( fix_record.getFullRecord() ) #write the fix
                #record the fix in the log file
                fh_log = open( self.log_file, "a", encoding = "utf-8" )
                fh_log.write("Line: {}\nOriginal: {}Fix: {}\n".format( self.line, self.problem_record, fix_record ) )
                fh_log.close()
            else: #did not locate the problem record, so just write out the line
                temp_fh.write( record.getFullRecord() )
        in_fh.close()
        temp_fh.close() #the temp file should now contain the fixes
        copyfile( self.temp_file, self.file ) #replace the original file with the temp file
        os.remove( self.temp_file ) #delete the temp file
        return
    
    def skipRecord( self, write_to_skip_file ):
        #add the line number to the dictionary that contains the list of line numbers to be skipped
        self.skipped_record_line_numbers[ self.line ] = True
        if write_to_skip_file:
            fh_skipped_file = open( self.skipped_file, "a", encoding = "utf-8" )
            fh_skipped_file.write( str( self.line ) + "\t" + self.problem_record.getFullRecord() )
            fh_skipped_file.close()

    def getCandidates( self, item ):
        #returns a listof tuples
        #each tuple contains a number 0, 1, 2, ... and a candidate
        candidates_list = self.corpus_dic.getCandidates( item )
        if candidates_list:
            temp = []
            for i, j in enumerate(candidates_list):
                temp.append( tuple( [str(i), j] ) )
            return temp
        else:
            return [ ("-1", "") ] #in the case of no candidates, return an empty string

