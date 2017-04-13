import file_handler as fh
import dictionary_handler as dh
import interface as i
import os

IN_DIR = "C:\\Users\\Kevin\\Dropbox\\Work\\python\\fixerGUI\\in\\"
OUT_DIR = "C:\\Users\\Kevin\\Dropbox\\Work\\python\\fixerGUI\\out\\"

############################
# main program
############################

# choose the file and prepare the SpeakerFile object
opened_file = i.fileOpener()
target_file = fh.SpeakerFile( opened_file )

# get the first problem record, create the GUI interface,
# edit one line, and then destroy the GUI interface
# repeat this over and over until the end of the file is reached
while True:
    try:
        target_file.getProblemRecord()
        gui_interface = i.Interface( target_file )
        gui_interface.build()
        gui_interface.start()
    except IOError:
        print("\n\nEnd of file. All done!\nMove the dic files back.\n")
        break
        
