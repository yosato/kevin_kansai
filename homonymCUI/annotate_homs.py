import os,imp,pickle,sys,json,glob,copy
import numpy as np
from termcolor import colored
#sys.path.append(os.path.join(RepoDir,'normalise_jp'))
HomeDir=os.getenv('HOMEPATH') if os.name=='nt' else os.getenv('HOME')
DefRepoDir=os.path.join(HomeDir,'kevin_kansai')

from mecabtools import mecabtools
import normalise_mecab

import pythonlib_ys
imp.reload(mecabtools)
imp.reload(pythonlib_ys)
imp.reload(normalise_mecab)

def main():    
    FPs,CHs,ResultDir=get_data(RepoDir)
    Name=input_name()
    PersRecord=register_or_retrieve_namedrecord(Name,ResultDir)
    clear()
    NewPersRecord=backend(Name,PersRecord,FPs,CHs)

def get_data(RepoDir):
    CorpusDir=os.path.join(RepoDir,'corpus_files')
    CHFP=os.path.join(CorpusDir,'clustered_homs.pickle')
    FPs=glob.glob(os.path.join(CorpusDir,'*.txt'))
    ResultDir=RepoDir+'/homonymCUI/results'
    if not os.path.isfile(CHFP) or not os.path.isdir(ResultDir) or not FPs:
        sys.exit('probably you use the wrong dir for repository')
    with open(CHFP,'br') as FSr:
        CHs= pickle.load(FSr)

    return FPs,CHs,ResultDir

def backend(Name,PersRecord,FPs,CHs):
    CHFreqsTotal=np.zeros(len(CHs))
    DoneFNs=PersRecord['done_fns']
    FPs=[FP for FP in FPs if os.path.basename(FP) not in DoneFNs]
    RemainingCnt=len(FPs)
    if RemainingCnt==0:
        print('すでに作業は完了しています')
        sys.exit()
    CHKeys=set([tuple(CH.cluster_on.values()) for CH in CHs])
    CHProns=[CHKey[-1] for CHKey in CHKeys]
    for Cntr,FP in enumerate(FPs):
        FN=os.path.basename(FP)
        print('現在のファイル '+FN)
        print('作業が必要なファイルは現在のものを含めてあと'+str(RemainingCnt)+'残っています')

        print();print()
        RecordPerFile,CHFreqsPerFile=annotate_homonyms(FP,CHs,CHProns,CHKeys,CHFreqsTotal)
        RemainingCnt-=1
        PersRecord['done_fns'].append(FN)
        PersRecord[FN]=RecordPerFile
        CHFreqsTotal=CHFreqsTotal+CHFreqsPerFile
        
        if RemainingCnt and not pythonlib_ys.main.prompt_loop_bool('ファイル一つ分の入力が完了しました。次を続けますか?',TO=20,Default=True):

            print('次回以降未完了部分を続けてください。')
            break

    save_record(Name,PersRecord)

    if RemainingCnt==0:
        print('すべてのファイルが完了しました。協力ありがとうございました')
    print('お疲れ様!!!')
    

def annotate_homonyms(FP,CHs,CHProns,CHKeys,CHFreqsTotal):
    def find_relv_ch(CHs,CHProns,CHKeys,SentLines):
        SentEls=pythonlib_ys.main.flatten_list([(lambda SentLine: [SentLine.split('\t')[0]]+SentLine.split('\t')[1].split(','))(SentLine) for SentLine in SentLines])
        PotProns=[CHPron for CHPron in CHProns if CHPron in SentEls]
        if not PotProns:
            return []
#        PotCHKeys=[CHKey for CHKey in CHKeys if CHKey[-1] in PotProns]
        RelvIndPairs=[]
        for SentInd,SentLine in enumerate(SentLines):
            Bool=False
            Orth,Rest=SentLine.split('\t')
            Fts=Rest.split(',')
            LineEls=[Orth]+Fts
            if not any(PotPron in LineEls for PotPron in PotProns):
                continue
            for CHInd,CH in enumerate(CHs):
                if all(CHEl in LineEls for CHEl in CH.cluster_on.values()):
                    Bool=True
                    break
            if Bool:
                RelvIndPairs.append((SentInd,CHInd))
        return RelvIndPairs

    CHFreqsPerFile=np.zeros((len(CHs)))
    RecordPerFile={'records':{},'errors':[]}
    PrcLines='';CurSentEls=[]
    for SentCntr,SentLines in enumerate(mecabtools.generate_sentchunks(FP)):
        Errors=[]
        RelvIndPairs=find_relv_ch(CHs,CHProns,CHKeys,SentLines)
        if not RelvIndPairs:
            pass
        else:
            Wds=[mecabtools.mecabline2mecabwd(SentLine,'corpus') for SentLine in SentLines]
            if any(Wd is None for Wd in Wds):
                continue
            Sent=mecabtools.MecabSentParse(Wds)
            (RelvSentInds,RelvCHInds)=zip(*RelvIndPairs)
            (RelvSentInds,RelvCHInds)=list(RelvSentInds),list(RelvCHInds)
            SentID=os.path.basename(FP)+'_'+str(SentCntr)
            OverThreshs=[]
            for Cntr,CHInd in enumerate(RelvCHInds):
                CHFreqsPerFile[CHInd]+=1
                if CHFreqsPerFile[CHInd]>3 or CHFreqsPerFile[CHInd]+CHFreqsTotal[CHInd]>10:
                    OverThreshs.append(Cntr)
            for OverThresh in OverThreshs[::-1]:
                RelvSentInds.pop(OverThresh)
                RelvCHInds.pop(OverThresh)
                RelvIndPairs=zip(RelvSentInds,RelvCHInds)
            if not RelvSentInds:
                continue
            else:
                RelvSentEls=[Wd.pronunciation for (Ind,Wd) in enumerate(Sent.wds) if Ind in RelvSentInds ]
                if all(RelvSentEl in PrvSentEls for RelvSentEl in RelvSentEls):
                    continue
            CurSentEls=[Wd.pronunciation if Ind in RelvSentInds else Wd.orth for (Ind,Wd) in enumerate(Sent.wds)]
            PrcSent=''.join([PrvLine.split('\t')[0] for PrvLine in PrcLines])
            if len(PrcSent)>90:
                PrcSent=PrcSent[-90:]
            RenderedCurSent=''.join(colour_hash_list(CurSentEls,RelvSentInds))
            RenderedSent='\n[直前の内容]...('+PrcSent+')\n'+RenderedCurSent
            print(RenderedSent)
            Inputs=[]
            for (Num,(RelvSentInd,RelvCHInd)) in enumerate(RelvIndPairs):
                ValidatedInput,NewCH=get_validate_input(Num,Sent.wds[RelvSentInd],CHs[RelvCHInd])
                if ValidatedInput is False:
                    Errors.append([SentID,Num])
                elif NewCH is not None:
                    CHs[RelvCHInd]=NewCH
                Inputs.append(ValidatedInput)
            RecordPerFile['records'][SentID]=Inputs
            RecordPerFile['errors'].extend(Errors)
            
            clear()
        PrcLines=SentLines
        PrvSentEls=CurSentEls
    print(FP+' done')
    return RecordPerFile,CHFreqsPerFile



def colour_hash_list(OrgLofStrs,RelvInds):
    LofStrs=copy.copy(OrgLofStrs)
    for Cntr,Ind in enumerate(RelvInds):
        LofStrs[Ind]=colour_string_cycle(LofStrs[Ind],Cntr,Prefix='##',Suffix='##')
    return LofStrs


def colour_string_cycle(Str,Cntr,Cycle=3,Prefix='',Suffix=''):
    Mod=Cntr%Cycle
    if Mod==0:
        Colour='blue'
    elif Mod==1:
        Colour='green'
    else:
        Colour='red'
    return colored(Prefix+Str+Suffix,Colour,attrs=['bold'])

def clear(): 
  
    # for windows 
    if os.name == 'nt': 
        _ = os.system('cls') 
  
    # for mac and linux(here, os.name is 'posix') 
    else: 
        _ = os.system('clear') 
  

def validate_input(OrgStr,Num,Delim=' '):
    if OrgStr.strip().lower()=='x':
        return False
    Str=''.join([pythonlib_ys.main.zenkaku_hankaku(Char) if ord(Char)>300 else Char for Char in OrgStr ])
    if ' ' not in Str:
        print('各ランクをスペースで区切ってください')
        return None
    Substrs=[Substr.strip() for Substr in Str.strip().split()]
    if any(not Substr.isnumeric() for Substr in Substrs):
        print('ランクは整数で入力してください')
        return None
    Ints=[int(Substr) for Substr in Substrs]
    ElCnt=len(Ints)
    if not ElCnt==Num:
      #  if ElCnt==Num-1:
       #     LastNum=10-sum(Ints)
        #    Ints.append(LastNum)
        #else:
        print('ランクは各項目につけてください')
        return None
    if sum(Ints)!=10:
        print('ランクは和が１０になるようにしてください')
        return None
    return Ints
def abc(num,StartChar='a',Delim=' '):
    alph=list('abcdefghijklmnopqprstuvwxyz')
    RetStr=[]
    StartInd=alph.index(StartChar)
    for i in range(num):
        RetStr.append(alph[StartInd+i])
    return Delim.join(RetStr)

def get_validate_input(Num,Wd,CH):
    InputValidP=False;NewCH=None
    while not InputValidP:
        print(colour_string_cycle(Wd.pronunciation,Num))
        OrthCands=list({Wd.orth for Wd in CH.all_words})
        if all(not pythonlib_ys.main.all_of_chartypes_p(Cand,['hiragana']) for Cand in OrthCands):
            OrthCands.append(CH.hiragana_rendering)
        if len(OrthCands)==2 and (pythonlib_ys.main.all_of_chartypes_p(OrthCands[0],['hiragana']) and pythonlib_ys.main.all_of_chartypes_p(OrthCands[1],['han']) or pythonlib_ys.main.all_of_chartypes_p(OrthCands[0],['han']) and pythonlib_ys.main.all_of_chartypes_p(OrthCands[1],['hiragana'])):
            OrthCands.append(pythonlib_ys.main.render_katakana(CH.hiragana_rendering))
        print(' '.join(OrthCands))
        InputStr=input('ランク(形式 '+abc(len(OrthCands),StartChar='m')+',自分で書き方を加える場合はn,データが間違っている場合はx): ')
            
        if InputStr=='n':
            InputOK=False
            while not InputOK:
                NewInput=input('加えたい書き方: ')
                if pythonlib_ys.main.prompt_loop_bool(NewInput.strip()+' でよろしいですか',Lang='jp'):
                    InputOK=True
                    OrthCands.append(NewInput)
                    print(' '.join(OrthCands))
                    InputStr=input('ランク(形式 '+abc(len(OrthCands),StartChar='m')+'): ')

                    ValidatedInput=validate_input(InputStr,len(OrthCands))
                    NewWd=CH.all_words[0]
                    NewCH=copy.deepcopy(CH)
                    NewWd.change_feats({'orth':NewInput})
                    NewCH.add_word(NewWd)
        else:
            ValidatedInput=validate_input(InputStr,len(OrthCands))
        if ValidatedInput:
            return dict(zip(OrthCands,ValidatedInput)),NewCH
        elif ValidatedInput is False:
            return None,None

def input_name():
    InputValid=False
    while not InputValid:
        Name=input('名前（ハンドルネーム可）を入力してください: ').strip()
        if not Name:
            continue
        InputValid=pythonlib_ys.main.prompt_loop_bool('名前は\n'+Name+'\nでよろしいですか。',TO=30,Lang='jp')
    return Name

def save_record(Name,Record):
    UserJson=os.path.join(ResultDir,'personalrecord_'+Name+'.json')
    open(UserJson,'wt').write(json.dumps(Record,ensure_ascii=False))
    print('ここまでの作業内容は保存されました。')
    
def register_or_retrieve_namedrecord(Name,ResultDir):
    InputValid=False
    while not InputValid:
        UserJson=os.path.join(ResultDir,'personalrecord_'+Name+'.json')
        if os.path.isfile(UserJson):
            if pythonlib_ys.main.prompt_loop_bool('その名前の記録が存在します。以前に作業をしていますか',Lang='jp'):
                InputValid=True
                PersRecord=json.load(open(UserJson))
            else:
                Name=input('別の名前（ハンドルネーム可）を入力してください: ')
        else:
            InputValid=pythonlib_ys.main.prompt_loop_bool('新たにこの名前('+Name+')を登録します。作業を続行するときのために覚えておいてください。別の名前にしたい場合はNoを選んでください',Default=True,TO=20,Lang='jp')
            if InputValid:
                PersRecord={'done_fns':[]}
            else:
                Name=input('別の名前（ハンドルネーム可）を入力してください: ')
    return PersRecord

if __name__=='__main__':
    if len(sys.argv)==2:
        DefRepoDir=sys.argv[1]
    if os.path.isdir(DefRepoDir):
        RepoDir=DefRepoDir
    else:
        Path=input('You do not have the repo in the normal place. Enter the path to the repo: ')
        if not os.path.isdir(Path):
            sys.exit('The path you entered do not exist')
        else:
            RepoDir=Path
    main()

