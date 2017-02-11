import sys,os,re,imp,subprocess
from  pythonlib_ys import main as myModule
import jp_morph

imp.reload(jp_morph)
imp.reload(myModule)

def main():
    import argparse
    ArgPsr=argparse.ArgumentParser()
    ArgPsr.add_argument('jsonfp')
    Args=ArgPsr.parse_args()
    
    main0(Args.jsonfp)

def main0(JsonFP,Debug=0):
    RawTxtFP=myModule.change_ext(JsonFP,'raw.txt')
    Cmd=' '.join(['jq .text', JsonFP, '''| sed 's/^"//;s/"$//' > ''', RawTxtFP ])
    Proc=subprocess.Popen(Cmd,shell=True)
    Return=Proc.wait()
    if Return!=0:
        sys.exit()
    
    Seen=set()
    with open(RawTxtFP) as FSr:
        for LiNe in FSr:
            NewLines=clean_line_with_defaults(LiNe.strip(),Debug)
    for Line in NewLines:
        if Line in Seen:
            sys.stderr.write('\nduplication'+Line+'\n')
            continue
        if len(Line)<=10:
            sys.stderr.write('\ntoo short  '+Line+'\n\n')
            continue
        #sys.stderr.write('\noutput\n')
        sys.stdout.write(Line+'\n')
        Seen.add(Line)

def clean_line_with_defaults(Line,Debug=0):
    RegexesToDel=(re.compile(r'https?://[a-zA-Z0-9%_/]*'),
                  re.compile(r'[@#][%_a-zA-Z0-9]+'),
                  re.compile(r'[\^_o()°;❤❤д○＼／|、…️]+$'),
                  re.compile(r'\(?[爆笑]\)?$'))
    RegexesToRepl=[(re.compile(r'[~〜]+'),'ー')]
    # punc -> linebreak later, inc. smileys
    #'ww+|(?^..*^)?|(?￣..*￣)?|
    PunctRegex=re.compile(r'\(..*\)|ww+|(\\n)+|[!? ！？　.♡。❤]')
    Banned=('♪')
    CodePointRange=(0,40959)
    return clean_line(Line,RegexesToDel,RegexesToRepl,PunctRegex,Banned,CodePointRange,Debug)
        
            
def clean_line(Line,RegexesToDel,RegexesToRepl,PunctRegex,Banned,CodePointRange,Debug):
    NewLines=[]
    sys.stderr.write('\noriginal '+Line+'\n\n')
    # delete nonjapanese tail
    Line=delete_nonjp_tail(Line)
    # reduction of multiple elongations
    Line=re.sub('ーー+','ー',Line)
    # mid-sent punctuation -> linebreak so that you get roughly a sentence a line
    Lines=[ L for L in re.split(PunctRegex,Line) if L ]
    #                          Lines=[ L for L in re.split(r'(\\n)+|[!? ！？　.。]',Line) if L ]

    if Debug:
        if len(NewLines)>=2:
            print('punctuation turned into linebreak')
            print(Lines)
        else:
            print('no punctuation inside the line')

    # these are supposed to be a sentence level
    for Line in Lines:
        if not myModule.at_least_one_of_chartypes_p(Line,['hiragana','katakana']):
            sys.stderr.write('no hiragana or katakana in this line '+Line+'\n')
            continue
        NewLine=''
        if Debug:   LineB4=Line
        for RegexToDel in RegexesToDel:
            Line=re.sub(RegexToDel,' ',Line)
        if Debug:
            print('after regexes to delete')
            if Line==LineB4:
                print('no change')
            else:
                print(Line)
                
        if Debug:    LineB4=Line    
        for (RegOrg,Tgt) in RegexesToRepl:
            Line=re.sub(RegOrg,Tgt,Line)
        if Debug:
            print('after regexes to replace')
            if Line==LineB4:
                print('no change')
            else:
                print(Line)

        # reduce the repetition of the same characters to one    
        if Debug:    LineB4=Line
        Line=re.sub(r'([あいうえおアイウエオ])\1{4,}',r'\1',Line)
        if Debug:
            print('after repetition reduction')
            if Line==LineB4:
                print('no change')
            else:
                print(Line)

        PrvChar=''; LineLen=len(Line)
        if Debug:    LineB4=Line
        for CharCntr,Char in enumerate(Line):
            CodePDec=ord(Char)
            if CodePDec>40959 or (CodePDec>=9728 and CodePDec<=9983) or Char in Banned:
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
        
        if Debug:
            print('after character-based changes')
            if NewLine==LineB4:
                print('no change')
            else:
                print(NewLine)

        NewLines.append(NewLine)

    return NewLines
                
def delete_or_replace(PrvChar,NextChar):
    Wds=[('で','す'), ('ま','す'), ('さ','ん'), ('ゃ','ん'), ('た','い',),('な','',),('た','',),('ね',''),('の',''),('よ','')]
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

def delete_nonjp_tail(Str):
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
