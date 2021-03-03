import os,sys,glob,imp
from mecabtools import mecabtools
imp.reload(mecabtools)

global NativeCoprusFPs,RyugakuseiCorpusFPs
ParentDir=os.path.dirname(os.path.abspath('.'))
NativeCorpusFPs=glob.glob(ParentDir+'/native/*.txt')
RyugakuseiCorpusFPs=glob.glob(ParentDir+'/ryugakusei/*.txt')

def create_simplemecab_bulk(FPs):
    assert len(set([os.path.dirname(FP) for FP in FPs]))==1
    OutDir=os.path.join(os.path.dirname(FPs[0]),'simplemecab')
    if not os.path.isdir(OutDir):
        os.makedirs(OutDir)
    apply_function(lambda FP:create_simplemecab(FP,OutDir),FPs) 

def check_validity_bulk(FPs):
    apply_function(check_validity,FPs)
    
def check_validity(FP):
    InvLines=mecabtools.invalid_lines_mecabfile(FP,"corpus")
    if InvLines:
        print(FP)
        apply_function(print,InvLines)
    ValidP=False if InvLines else True
    return ValidP
        
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
    for Set in (NativeCorpusFPs,RyugakuseiCorpusFPs):
        create_simplemecab_bulk(Set)
