import os,imp,pickle,sys,json,glob
import numpy as np
from termcolor import colored

# this needs to be adapted Kevin
#RepoRt='/Users/yosato/myProjects_maclocal'
RepoRt='/cygwin64/home/motok'

RepoDir=os.path.join(RepoRt,'kevin_kansai')

sys.path.append(os.path.join(RepoDir,'myPythonLibs'))
sys.path.append(os.path.join(RepoDir,'normalise_jp'))

from mecabtools import mecabtools
import normalise_mecab

import pythonlib_ys
imp.reload(mecabtools)
imp.reload(pythonlib_ys)

global ResultDir
ResultDir=os.getenv('HOMEPATH')


global MecabDir
MecabDir=os.path.join(RepoDir,'corpus_files')
FPs=glob.glob(os.path.join(MecabDir,'[KT]*.txt'))
#FPs=glob.glob(os.path.join(MecabDir,'aiueo*.txt'))

if not FPs:
    sys.exit('probably you get the wrong RepoDir\n\n')

with open(os.path.join(RepoDir,'clustered_homs.pickle'),'br') as FSr:
    CHs= pickle.load(FSr)

def main():    
    Name=input_name()
    PersRecord=register_or_retrieve_namedrecord(Name,ResultDir)
    clear()
    NewPersRecord=backend(Name,PersRecord,FPs,CHs)
    
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
    PrvLines=''
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
            PrvSent=''.join([PrvLine.split('\t')[0] for PrvLine in PrvLines])
            if len(PrvSent)>90:
                PrvSent=PrvSent[-90:]
            RenderedSent='\n[直前の内容]...('+PrvSent+')\n'+''.join([colour_string_cycle('##'+Wd.pronunciation+'##',RelvSentInds.index(Ind)+1) if Ind in RelvSentInds else Wd.orth for (Ind,Wd) in enumerate(Sent.wds)])
            print(RenderedSent)
            Inputs=[]
            for (Num,(RelvSentInd,RelvCHInd)) in enumerate(RelvIndPairs):
                ValidatedInput=get_validate_input(Num+1,Sent.wds[RelvSentInd],CHs[RelvCHInd])
                if ValidatedInput is False:
                    Errors.append([SentID,Num])
                Inputs.append(ValidatedInput)
            RecordPerFile['records'][SentID]=Inputs
            RecordPerFile['errors'].extend(Errors)
            
            clear()
        PrvLines=SentLines
    print(FP+' done')
    return RecordPerFile,CHFreqsPerFile

def colour_string_cycle(Str,Cycle):
    Mod=Cycle%3
    if Mod==0:
        Colour='blue'
    elif Mod==1:
        Colour='green'
    else:
        Colour='red'
    return colored(Str,Colour,attrs=['bold'])

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
    InputValidP=False
    while not InputValidP:
        print(colour_string_cycle(Wd.pronunciation,Num))
        OrthCands=list({Wd.orth for Wd in CH.all_words})
        print(' '.join(OrthCands))
        CandCnt=len(OrthCands)
        InputStr=input('ランク(形式 '+abc(CandCnt,StartChar='m')+',判定不能の場合x): ')
        ValidatedInput=validate_input(InputStr,CandCnt)
        if ValidatedInput:
            return dict(zip(OrthCands,ValidatedInput))
        elif ValidatedInput is False:
            return False

    
    

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
    main()

