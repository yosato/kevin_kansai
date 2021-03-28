import os,sys,glob,imp
from mecabtools import mecabtools
imp.reload(mecabtools)

global NativeCorpusFPs,RyugakuseiCorpusFPs
ParentDir=os.path.dirname(os.path.abspath('.'))
NativeCorpusFPs=glob.glob(ParentDir+'/native/*.txt')
RyugakuseiCorpusFPs=glob.glob(ParentDir+'/ryugakusei/*.txt')
FtsRepls={
    (('cat','動詞'),('pronunciation','ユウ')):{'pronunciation':'イウ'}
}

def all_samedir(FPs):
    return len(set([os.path.dirname(FP) for FP in FPs]))==1

def k2y_bulk(FPs,FtsRepls):
    assert FPs
    assert all_samedir(FPs)
    OutDir=os.path.dirname(FPs[0])
    apply_function(lambda FPs:k2y_file(FPs,FtsRepls,OutDir),FPs)

def create_simplemecab_bulk(FPs):
    assert all_samedir(FPs)
    OutDir=os.path.join(os.path.dirname(FPs[0]),'simplemecab')
    if not os.path.isdir(OutDir):
        os.makedirs(OutDir)
    apply_function(lambda FP:create_simplemecab(FP,OutDir),FPs) 

def check_validity_bulk(FPs):
    return all(map(check_validity,FPs))

def get_invalid_fps(FPs):
    Valids=map(check_validity,FPs)
    if all(Valids):
        return []
    else:
        InvalidInds=[Ind for (Ind,Bool) in enumerate(Valids) if not Bool]
        return [FP for (Ind,FP) in enumerate(FPs) if Ind in InvalidInds] 
    
def check_validity(FP):
    InvLines=mecabtools.invalid_lines_mecabfile(FP,"corpus")
    if InvLines:
        print(FP)
        apply_function(print,InvLines)
    ValidP=False if InvLines else True
    return ValidP

def k2y_file(FP,FtsRepls,OutDir):
    FSw=open(os.path.join(OutDir,os.path.basename(FP)+'.simplemecab'),'wt')
    for SentChunk in mecabtools.generate_sentchunks(FP):
#        NewSent=map(lambda Line:k2y_line(Line,FtsRepls),SentChunk)
        NewSent=[]
        for Line in SentChunk:
            NewLine=k2y_line(Line,FtsRepls)
            NewSent.append(NewLine)
        FSw.write('\n'.join(NewSent))
    FSw.close()

def k2y_line(Line,FtsRepls):
    SetsOfFtsVals=FtsRepls.keys()
    RelvFeatSet=next((FtsVals for FtsVals in SetsOfFtsVals if mecabtools.featsvals_in_line_p(Line,FtsVals,InhFtNamesToAdd=['speaker_role'])), None)
    if RelvFeatSet:
        MWd=mecabtools.mecabline2mecabwd(Line)
        MWd.change_feats(FtsRepls[RelvFeatSet])
        return MWd.get_mecabline
    else:
        return Line
    
def lemmatise_variants(Line):
    #to be implemented
    pass

def create_simplemecab(FP,OutDir):
    FSw=open(os.path.join(OutDir,os.path.basename(FP)+'.simplemecab'),'wt')
    for SentChunk in mecabtools.generate_sentchunks(FP):
        SentEls=[]
        for Line in SentChunk:
            FtsVals=mecabtools.line2wdfts(Line)
            RelvFts=FtsVals['orth'],FtsVals['cat'],FtsVals['subcat']
            SentEls.append('/'.join(RelvFts))
        FSw.write(' '.join(SentEls)+'\n')
    FSw.close()

def apply_function(func,List):
    for El in List:
        func(El)
        

    
if __name__=='__main__':
    pass

## k2y
    k2y_bulk(NativeCorpusFPs,FtsRepls)
## checking validity


## creating simple version of mecab
#    for Set in (NativeCorpusFPs,RyugakuseiCorpusFPs):
#        create_simplemecab_bulk(Set)
