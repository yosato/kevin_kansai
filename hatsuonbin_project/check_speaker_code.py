import os
import speaker_record as r

in_dir = os.path.dirname(__file__) + "\\corpus_data_rgs\\"
files = os.listdir( in_dir )
for file in files:
    print( file )
    full_file_name = in_dir + file
    fh_in = open( full_file_name, "r", encoding = "utf-8" )
    while True:
        data_line = fh_in.readline()
        if data_line == "": break
        try:
            data_record = r.Record( data_line )
        except:
            print("Error in:", data_line)
            raise
        #if data_record.speaker == "s":            
    fh_in.close()

