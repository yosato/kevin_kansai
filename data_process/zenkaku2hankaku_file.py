import sys,os,imp
from pythonlib_ys import main as myModule
imp.reload(myModule)

def main0(FP):
    FSw=open(FP+'.zenkakunormed','wt')
    for LiNe in open(FP):
        FstZenkakuInd=myModule.first_zenkaku_ind(LiNe)
        if FstZenkakuInd==-1:
            FSw.write(LiNe)
        else:
            NewLiNe=LiNe[:FstZenkakuInd]
            for Char in LiNe.strip()[FstZenkakuInd:]:
                ConvertedOrNot=myModule.zenkaku_hankaku(Char)
                if not ConvertedOrNot:
                    NewLiNe+=Char
                else:
                    NewLiNe+=ConvertedOrNot
            NewLiNe+='\n'
            FSw.write(NewLiNe)

    FSw.close()

def main():

    if len(sys.argv)!=2:
        sys.exit('arg for fp necessary')
    FP=sys.argv[1]
    if not os.path.isfile(FP):
        sys.exit(FP+' does not exist\n')
    main0(FP)

if __name__=='__main__':
    main()
