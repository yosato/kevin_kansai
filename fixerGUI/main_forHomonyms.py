import os,imp,pickle,sys
sys.path.append('../normalise_jp')
import normalise_mecab
import file_handler2 as fh
#import dictionary_handler as dh
import interface_forHomonyms as i

imp.reload(normalise_mecab)
imp.reload(fh)
imp.reload(i)

IN_DIR = os.path.dirname(__file__) + "/in"
OUT_DIR = os.path.dirname(__file__) + "/out"

print(IN_DIR)

############################
# main program
############################

# choose the file and prepare the SpeakerFile object
#opened_file = i.fileOpener()
myDir='/Users/yosato/myProjects_maclocal/kevin_kansai'
with open(os.path.join(myDir,'clustered_homs.pickle'),'br') as FSr:
    clustered_homs= pickle.load(FSr)
fp=os.path.join(myDir,'corpus_files/KSJ073M7.txt')
target_file = fh.SpeakerFile( fp )

# get the first problem record, create the GUI interface,
# edit one line, and then destroy the GUI interface
# repeat this over and over until the end of the file is reached
while True:
    try:
       # target_file.getProblemRecord()
        gui_interface = i.Interface( target_file, clustered_homs )
        gui_interface.build()
        gui_interface.start()
    except IOError:
        print("\n\nEnd of file. All done!\nMove the dic files back.\n")
        break
        
