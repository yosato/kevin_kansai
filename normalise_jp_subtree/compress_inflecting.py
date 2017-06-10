import imp,re,sys,os, subprocess
import romkan
import mecabtools
from pythonlib_ys import main as myModule
from pythonlib_ys import jp_morph
imp.reload(mecabtools)
imp.reload(jp_morph)

#Debug=2

def main0(MecabFP,CorpusOrDic='dic',OutFP=None,Debug=0,Fts=None,UnkAbsFtCnt=2,StrictP=False):
    NewWds=set()
    if OutFP is True:
        Stem,Ext=myModule.get_stem_ext(MecabFP)
        Out=open(Stem+'.compressed.'+Ext,'wt')
    elif OutFP is None or OutFP is False:
        Out=sys.stdout
    else:
        Out=open(OutFP+'.tmp','wt')

    ChunkGen=generate_chunks(MecabFP,CorpusOrDic)

    ErrorStrs=[]
    for Cntr,SentChunk in enumerate(ChunkGen):
        if not SentChunk:
            if Debug:
                sys.stderr.write('\nsent '+str(Cntr+1)+' is empty\n')
            continue
        if Debug:
            sys.stderr.write('\nsent '+str(Cntr+1)+' '+''.join([Sent.split('\t')[0] for Sent in SentChunk])+'\n')
        SuccessP,NewLines=lemmatise_mecabchunk(SentChunk,CorpusOrDic,NewWds,OutFP,Debug=Debug,Fts=Fts,UnkAbsFtCnt=UnkAbsFtCnt)
        if SuccessP:
            Out.write('\n'.join(NewLines+['EOS'])+'\n')
        else:
            if StrictP:
                lemmatise_mecabchunk(SentChunk,CorpusOrDic,NewWds,OutFP,Debug=2,Fts=Fts)
            else:
                ErrorStr='sentence '+str(Cntr+1)+' failed\n'+repr(SentChunk)+'\non: '+repr(NewLines.__dict__)
                sys.stderr.write('\n'+ErrorStr+'\n')
                ErrorStrs.append(ErrorStr)
    if OutFP:
        Out.close()
        os.rename(OutFP+'.tmp',OutFP)

        if ErrorStrs:
            ErrorOut=open(OutFP+'.errors','wt')
            ErrorOut.write('\n'.join(ErrorStrs))

def sort_mecabdic_fts(MecabDicFP,Inds,OutFP):
    if not all(os.path.exists(FP) for FP in (MecabDicFP,os.path.dirname(OutFP))):
        sys.exit('one of the files does not exist')
    
    Cmd=' '.join(['cat', MecabDicFP, '| sort -k', ' '.join([str(Ind) for Ind in Inds]), '>', OutFP ])
    Proc=subprocess.Popen(Cmd,shell=True)
    Proc.communicate()
            
def generate_ftchunk(MecabDicFP,FtInds,Out=sys.stdout):
    SortedDicFP=myModule.get_stem_ext(MecabDicFP.replace('rawData','processedData'))[0]+'.sorted.csv'
    sort_mecabdic_fts(MecabDicFP,FtInds,OutFP=SortedDicFP)
    FSr=open(SortedDicFP)
    Lines=[];PrvRelvFts=None;FstLoop=True
    for LiNe in FSr:
        if not FstLoop:
            Line=LiNe.strip()
            LineEls=Line.split(',')
            RelvFts=[LineEls[Ind] for Ind in FtInds]
            if PrvRelvFts!=RelvFts:
                yield Lines
                Lines=[]
            else:
                Lines.append(Line)
                PrvRelvFts=RelvFts
        else:
            FstLoop=not FstLoop

def generate_chunks(MecabFP,CorpusOrDic):
    if CorpusOrDic=='dic':
        return generate_ftchunk(MecabFP,[-1])
    elif CorpusOrDic=='corpus':
        return mecabtools.generate_sentchunks(MecabFP)
    else:
        sys.exit('type must be either corpus or dic')
        
def lemmatise_mecabchunk(SentChunk,CorpusOrDic,NewWds,OutFP,Fts=None,UnkAbsFtCnt=2,Debug=0):
    NewLines=[]
    for Cntr,Line in enumerate(SentChunk):
        if Debug>=2:  sys.stderr.write('Org line: '+Line+'\n')
        if CorpusOrDic=='corpus' and Line=='EOS':
            AsIs=True
        else:
            FtsVals=mecabtools.pick_feats_fromline(Line,('cat','infpat','infform'),CorpusOrDic=CorpusOrDic,Fts=Fts)
            FtsValsDic=dict(FtsVals)
            #most of the time, you don't compress
            AsIs=True
            if FtsValsDic['cat'] in ('動詞','形容詞','助動詞'):
                # but if they're inflecting, you usually compress
                AsIs=False
                #except it is ichidan renyo and mizen
                if (FtsValsDic['infpat']=='一段' and FtsValsDic['infform'] in ('連用形','未然形')) or FtsValsDic['infpat']=='不変化型' or FtsValsDic['infpat']=='特殊・ヌ':
                    AsIs=True
        if AsIs:
            ToWrite=[Line]
            if Debug>=2:   sys.stderr.write('no change\n')
        else:
            if Debug>=2:
                print('\nPotentially compressable line '+str(Cntr+1)+'\n'+Line+'\n\n')
            OrgWd=mecabtools.mecabline2mecabwd(Line,Fts=Fts,CorpusOrDic=CorpusOrDic,WithCost=True)
            # THIS IS WHERE RENDERING HAPPENS
            try:
                NewWd,Suffix=OrgWd.divide_stem_suffix_radical()
            except:
                FailedWd=OrgWd
                return (False,FailedWd)
                #OrgWd.divide_stem_suffix_radical()

            NecEls=(NewWd.orth,NewWd.cat,NewWd.subcat,NewWd.infpat,NewWd.infform,NewWd.reading)

            if CorpusOrDic=='dic' and NecEls in NewWds:
                if Debug>=2:
                    sys.stderr.write('Not rendered, already found\n')
                ToWrite=''
            else:
                if Debug>=1:
                    print('Rendered, '+OrgWd.orth+' ->'+NewWd.orth+'\n')
                if CorpusOrDic=='dic':
                    NewWds.add(NecEls)
                    ToWrite=[Line]
                else:
                    ToWrite=[ Wd.get_mecabline(CorpusOrDic='corpus') for Wd in (NewWd,Suffix) if Wd.orth ]
                if Debug:    sys.stderr.write('rendered: '+'\n'.join(ToWrite)+'\n')

        NewLines.extend(ToWrite)
    return (True,NewLines)

        
#SuffixDicFP='/home/yosato/links/myData/mecabStdJp/dics/compressed/suffixes.csv'
#SuffixWds=[ mecabtools.mecabline2mecabwd(Line,CorpusOrDic='dic') for Line in open(SuffixDicFP) ]

def nonstem_wd_p(Wd):
    DefBool=False
    if any(Wd.infform==Form for Form in ('未然特殊','連用タ接続')) or Wd.infpat=='一段' and any(Wd.infform==Form for Form in ('連用','未然')):
        return not DefBool
    return DefBool

def already_seen(NewWd,Wds):
    DefBool=False
    for Wd in Wds:
        if Wd.feature_identical(NewWd,Excepts=('costs')):
            return not DefBool
    return DefBool

def main():
    import argparse
    APsr=argparse.ArgumentParser(description='''
      compress mecab dic/corpus inflecting items on mecab dic/corpus
      does *not* do the mecab parsing itself (use the wrapper, compress_normalise_jp.py if you start from the raw corpus)
    ''')
    APsr.add_argument('mecab_fp')
    APsr.add_argument('--out-fp',default=None)
    APsr.add_argument('--debug',type=int,default=1)
    Args=APsr.parse_args()

    if Args.mecab_fp.endswith('.csv'):
        CorpusOrDic='dic'
    elif Args.mecab_fp.endswith('.mecab'):
        CorpusOrDic='corpus'
    else:
        sys.exit('\n\nmecabfile should end with either csv (dic) or mecab (corpus)\n\n')
    if Args.out_fp=='True':
        OutFP=True
    else:
        OutFP=Args.out_fp
        
    main0(Args.mecab_fp,CorpusOrDic=CorpusOrDic,OutFP=OutFP,Debug=Args.debug)
    
if __name__=='__main__':
    main()
