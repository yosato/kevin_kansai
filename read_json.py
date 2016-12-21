import sys,os,json

def main(FP):
    with open(FP) as FSr:
        for LiNe in FSr:
            Dict=json.loads(LiNe)
            Strs=[ (str(Key)+': '+str(Val)) for (Key,Val) in Dict.items() ]
            Str='\n'.join(Strs)
            print('\n'+Str+'\n')
            
    

if __name__=='__main__':
    Args=sys.argv
    if len(Args)<2:
        sys.exit('\nnecessary arg missing (filepath)\n')
    FP=Args[1]

    if not os.path.isfile(FP):
        sys.exit('\nfile does not exist ('+FP+')\n')
    main(FP)
