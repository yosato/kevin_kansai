import re,sys

def replace_nthsonly(Str,RegexOldSubStr,RegexNewSubStr,Nths):
    NewStr='';i=0
    while Str:
        Match=re.match(RegexOldSubStr,Str)
        if Match:
            i=len(Match.group(0))
            NewStr+=re.sub(RegexOldSubStr,RegexNewSubStr,Str)
        else:
            i+=1
            NewStr+=Str[0]
        Str=Str[i:]

#A=re.compile(r'(ca[tp])')
#replace_nthsonly('aa-cat-bb-cak-cc-cap-dd-cat-ee',A,r'\1 ',[1,3])

def split_longsent(Str,Thr,Puncts):
    NumDivs=(len(Str)//Thr)+1
    PunctCnt=len([ Char for Char in Str if Char in Puncts])
    UnitCnt=(PunctCnt//NumDivs)+1
    UnitCnts=[ UnitCnt*NumDiv for NumDiv in range(1,NumDivs) ]
    PunctCntr=0
    NewStr=''
    for Char in Str:
        if Char not in Puncts:
            NewStr+=Char
        else:
            PunctCntr+=1
            if PunctCntr not in UnitCnts:
                NewStr+=Char
            else:
                NewStr+=Char+'\n'
    return NewStr

def main0(FP,Thr=500):
    Puncts=list('!?。 　')
    #FSw=open(FP+'.longdiv','wt')
    for LiNe in open(FP):
        Chars=list(LiNe.strip())
        Len=len(Chars)
        if Len>Thr:
            NewLiNe=split_longsent(LiNe,Thr,Puncts)
            sys.stdout.write(NewLiNe)
        else:
            sys.stdout.write(LiNe)
    

def main():
    FP=sys.argv[1]
    main0(FP)

if __name__=='__main__':
    main()
