import sys,re,imp,subprocess
#from pythonlib_ys import main as myModule
#from pythonlib_ys import jp_morph

my_module_file = '/home/yosato/myProjects/kevin_kansai/myPythonLibs_subtree/pythonlib_ys/main.py'
jpmorph_file = '/home/yosato/myProjects/kevin_kansai/myPythonLibs_subtree/pythonlib_ys/jp_morph.py'

# Load the hi module using imp
myModuleMod = imp.load_source('myModule', my_module_file)
jp_morphMod = imp.load_source('jp_morph', jpmorph_file)

# Now this works, and prints hi!
import myModule
import jp_morph

def main():
    import argparse
    ArgPsr=argparse.ArgumentParser()
    ArgPsr.add_argument('jsonfp')
    Args=ArgPsr.parse_args()
    main0(Args.jsonfp)

def main0(JsonFP,OutFP=None,Debug=0):
    RawTxtFP=myModule.change_ext(JsonFP,'raw.txt')
    Cmd=' '.join(['jq .text', JsonFP, '''| sed 's/^"//;s/"$//' > ''', RawTxtFP ])
    Proc=subprocess.Popen(Cmd,shell=True)
    Return=Proc.wait()
    if Return!=0:
        sys.exit()

    if not OutFP:
        OutFP=myModule.get_stem_ext(JsonFP)[0]+'.parallel'
    Seen=set()
    with open(RawTxtFP) as FSr:
        with open(OutFP,'wt') as FSw:
            for LiNe in FSr:
                if Debug:   sys.stderr.write('\n\n'+LiNe+'\n')
                Line=LiNe.strip()
                if Line in Seen:
                    print('this line has already been encountered, skipping')
                    NewLines=[]
                else:
                    OldLines,NewLines=clean_line_with_defaults(Line,Debug,LogFSw=FSw)
                    assert(len(OldLines)==len(NewLines))
                    Seen.add(Line)
                    for OldLine,NewLine in zip(OldLines,NewLines):
                        if OldLine=='\\n':
                            continue
                        elif not NewLine:
                            Comment='EMPTIED'
                        elif OldLine==NewLine:
                            Comment='NO CHANGE'
                        else:
                            Comment='MODIFIED'
                        FSw.write('\t'.join([Comment,OldLine,NewLine])+'\n')
                        if NewLine:
                            sys.stdout.write(NewLine+'\n')


def clean_line_with_defaults(Line,Debug=0,LogFSw=None):
    #patterns to be removed
    RegexesToDel=(re.compile(r'https?://[a-zA-Z0-9%_/]*'),
                  re.compile(r'[@#][%_a-zA-Z0-9]+'),
                  re.compile(r'[\*#\^_o()°;❤❤д○\\＼／|、…️]+$'),
                  re.compile(r'^[\*#\^_o()°;❤❤д○\\＼／|、…️]+'),
                  re.compile(r'\(?[爆笑]\)?$'),)
    #patterns to be replaced
    RegexesToRepl=[(re.compile(r'[~〜]+'),'ー'),
                   (re.compile(r'ーー+'),'ー'),
                   (re.compile(r'([でま])ーす'),r'\1す'),
                   (re.compile(r'([あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもらりるれろわんがぎぐげござじずぜぞだぢづでどばびぶべぼぱぴぷぺぽ])ー$'),r'\1')
                  ]
    # punc -> linebreak later, inc. smileys
    #'ww+|(?^..*^)?|(?￣..*￣)?|
    PunctRegex=re.compile(r'\(..*\)|ww+|(\\n)+|[!? ！？♡。❤]')
    BannedChars=(('♪'),
                 ([(9728,9983),(40959,10000*10000)]))
    return clean_line(Line,(RegexesToDel,RegexesToRepl),PunctRegex,BannedChars,Debug,LogFSw=LogFSw)
        
            
def clean_line(Line,RegexSets,PunctRegex,Banned,Debug,LogFSw=None):
    Out=sys.stderr if not LogFSw else LogFSw
    def to_ignore_p(Line):
        DefBool=False
        if not Line.strip():
            return True
        if len(Line)<=3:
            Out.write('line too short: '+Line+'\n')
            return True
        if not myModule.at_least_one_of_chartypes_p(Line,['hiragana','katakana']):
            Out.write('no hiragana or katakana in this line: '+Line+'\n')
            return True
        return DefBool

    def regex_based_cleaning(Line,RegexSets):
        (RegexesToDel,RegexesToRepl)=RegexSets
        for RegexToDel in RegexesToDel:
            Line=re.sub(RegexToDel,' ',Line)
        for (RegOrg,Tgt) in RegexesToRepl:
            Line=re.sub(RegOrg,Tgt,Line)
        return Line
    
    def repetition_reduction(Line):
        return re.sub(r'([あいうえおぁぃぅぇぉアイウエオァィゥェォ])\1{3,}',r'\1',Line)

    # mid-sent punctuation -> linebreak so that you get roughly a sentence a line
    Lines=[ L.strip() for L in re.split(PunctRegex,Line) if L ]

    if Debug:
        if len(Lines)>=2:
            print('punctuation turned into linebreak')
            print(Lines)
        else:
            print('no punctuation inside the line')

    # these are supposed to be a sentence level
    NewLines=[]
    for Line in Lines:
        Line=remove_nonjp_tail(Line)
        # some sents are excluded
        if to_ignore_p(Line):
            NewLines.append('')
            continue

        Line=regex_based_cleaning(Line,RegexSets) if not Debug else myModule.execute_warn_ifdifferent(regex_based_cleaning,(Line,RegexSets,),0,'regex based cleaning')

        # reduce the repetition of the same characters to one
        Line=repetition_reduction(Line) if not Debug else myModule.execute_warn_ifdifferent(repetition_reduction,(Line,),0,'repetition reduction')

        Line=character_based_cleaning(Line,Banned) if not Debug else myModule.execute_warn_ifdifferent(character_based_cleaning,(Line,Banned,),0,'character based cleaning')

        NewLines.append(Line.strip())

    return Lines,NewLines


def character_based_cleaning(Line,BannedChars):
    NewLine=''
    PrvChar=''; LineLen=len(Line)

    for CharCntr,Char in enumerate(Line):
        if Char in BannedChars[0] or myModule.in_ranges(ord(Char),BannedChars[1]):
            NewLine+=' '
        else:
            if CharCntr!=0 and Char=='ー':
                NextChar=('' if CharCntr+1==LineLen else Line[CharCntr+1])
                WhatToDo=delete_or_replace(PrvChar,NextChar)
                if WhatToDo=='replace':
                    NewLine+=replace_elongation(PrvChar)
                elif WhatToDo=='donothing':
                    NewLine+=Char
            else:
                NewLine+=Char

        PrvChar=Char

    NewLine=NewLine.strip()
    return NewLine



def delete_or_replace(PrvChar,NextChar):
    Wds=[('で','す'), ('ま','す'), ('さ','ん'), ('ゃ','ん'), ('た','い',)]
    if myModule.identify_chartype(PrvChar)!='hiragana':
        return 'donothing'
    else:
        if (PrvChar,NextChar,) in Wds:
            return 'delete'
        else:
            return 'replace'

def replace_elongation(PrvChar):
    Dan=jp_morph.identify_dan(PrvChar)
    if Dan=='a':
        return 'あ'
    elif Dan=='i':
        return 'い'
    elif Dan=='e':
        return 'え'
    else:
        return 'う'

def remove_nonjp_tail(Str):
    Str=Str.strip()
    TailNJCntr=0
    for Cntr,Char in enumerate(Str[::-1]):
        if myModule.identify_chartype(Char) not in ('katakana','hiragana','han','cjksym','asciisym'):
            TailNJCntr+=1
        else:
            break
    if TailNJCntr==0:
        return Str
    else:
        return Str[:-TailNJCntr]
    
                
if __name__=='__main__':
    FP=sys.argv[1]
    main()
