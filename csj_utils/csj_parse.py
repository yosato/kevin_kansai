from xml.etree import ElementTree as ET
import os,sys,imp,glob,re,itertools
from collections import defaultdict,OrderedDict
sys.path.append('/home/yosato/myProjects/myPythonLibs')
from pythonlib_ys import main as myModule

imp.reload(myModule)

def main0(InFPs,Debug=False):
    Stats={'adj':[0,0],'others':[0,0],'pp':[0,0],'relcl':[0,0],'compl':[0,0]}
    FailedFPs=[]
    
    for XmlFP in InFPs:
        try:
            CompNomsPerFile=count_complex_nominals(XmlFP,Debug=Debug)
        except:
            FailedFPs.append(XmlFP)
        for (Type,Chains) in CompNomsPerFile.items():
            Stats[Type][0]+=len(Chains)
            WdCnt=sum(len(Chain) for Chain in Chains)
            Stats[Type][1]+=WdCnt

    output_stats(Stats)

def output_stats(Stats):
    TotalPhrs=sum([Cnts[0] for Cnts in Stats.values()])
    TotalWds=sum([Cnts[1] for Cnts in Stats.values()])
    
    print()
    for Type,Cnts in Stats.items():
        #print()
        PhrCnt=Cnts[0];WdCnt=Cnts[1]
        sys.stdout.write(Type+':\t'+str(PhrCnt)+' ('+str(round((PhrCnt/TotalPhrs)*100,3))+'%)\t'+str(WdCnt)+' ('+str(round((WdCnt/TotalWds)*100,3))+'%)\n')
    print()    
            

def count_complex_nominals(XmlFP,Debug=False):
    ComplexNominalsClassified={'relcl':[],'pp':[],'adj':[],'compl':[],'others':[]}
    for LUWsPerSent in generate_grouped_luws(XmlFP,Unit='Sentence'):
        if Debug:
            print_orths_from_luws(LUWsPerSent)
            sys.stdout.write('--------------------\n')
        ChainsLUW=get_dependency_chains(LUWsPerSent)
        if Debug:
            for Chain in ChainsLUW:
                print_orths_from_luws(Chain)
        NominalLUWChains=get_complex_nominals(ChainsLUW)
        LenGroupedNominalLUWChains=lengthgroup_chains(NominalLUWChains)
        for Chains in LenGroupedNominalLUWChains.values():
            if len(Chains)>=2:
                LengthSortedChains=sorted(Chains,key=lambda x:len(x),reverse=True)
            else:
                LengthSortedChains=Chains
            ChosenChain=LengthSortedChains[0]
            Class=classify_chain(ChosenChain)
            if Debug:
                sys.stdout.write(Class+'\t')
                print_orths_from_luws([stuff[1] for stuff in ChosenChain])
            ComplexNominalsClassified[Class].append(ChosenChain)

        if Debug:
            sys.stdout.write('========================\n')
    return ComplexNominalsClassified

def classify_chain(Chain):
    PenulPOS=Chain[-2][1].attrib['LUWPOS']
    if PenulPOS=='動詞':
        Class='relcl'
    elif PenulPOS=='名詞' or PenulPOS=='代名詞':
        Class='pp'
    elif PenulPOS=='形容詞' or PenulPOS=='連体詞':
        Class='adj'
    elif PenulPOS=='助詞':
        Class='compl'
    else:
        Class='others'
        #print_orths_from_luws(Chain)
        #print(PenulPOS)
    return Class

def lengthgroup_chains(Chains):
    NewChains=defaultdict(list)
    for Chain in Chains:
        TailInd=Chain[-1][0]
        NewChains[TailInd].append(Chain)
        
    return NewChains

def get_complex_nominals(ChainsLUW,Debug=False):
    ComplexNominals=[]
    for Chain in ChainsLUW:
        HitInds=[]
        for Cntr,(Ind,LUW) in enumerate(Chain):
            if 'LUWPOS' not in LUW.attrib.keys():
                return []
            else:
                POS=LUW.attrib['LUWPOS']
            if POS in ['名詞','代名詞']:
                HitInds.append(Cntr)
        if HitInds:
            LstNounInd=HitInds[-1]
            if LstNounInd>0:
                if Debug:
                    for LUW in Chain:
                        print(get_suws(LUW)[0].attrib)
                ComplexNominals.append(Chain[:LstNounInd+1])
    return ComplexNominals    

def print_orth_from_luw(LUW,Delim=' '):
    Strs=[]
    for SUW in get_suws(LUW):
        Strs.append(SUW.attrib['OrthographicTranscription'])
    sys.stdout.write(Delim.join(Strs)+Delim*3)


def print_orths_from_luws(LUWs,Delim='\n'):
    for Cntr,LUW in enumerate(LUWs):
        if len(LUW)==2:
            LUW=LUW[1]
        print_orth_from_luw(LUW)
    sys.stdout.write(Delim)

def get_suws(LUW):
    return [Child for Child in LUW if Child.tag=='SUW']

def get_dependency_chains(LUWsPerSent):
    ChainsNum=extract_dep_chain_from_luws(LUWsPerSent)
    ChainsLUW=[]
    for ChainNum in ChainsNum:
        ChainsLUW.append([(Ind,LUWsPerSent[Ind]) for Ind in ChainNum])
    return ChainsLUW        

def find_next_connections(OrgPair,TgtPairs):
    return [Pair for Pair in TgtPairs if Pair[0]==OrgPair[1]]
    


def extract_dep_chain_from_luws(LUWsPerSent):
    MderIDs=[];MdedIDs=[]
    for LUWCntr,LUW in enumerate(LUWsPerSent):
        MderID,MdedID=[(Ind,int(Ft)) if Ft is not None else None for Ind,Ft in get_next_suwfeats_withinds(LUW,['Dep_BunsetsuUnitID','Dep_ModifieeBunsetsuUnitID'])]
        if MderID:
            MderIDs.append(((LUWCntr,)+(MderID[0],),MderID[1]))
        if MdedID:
            MdedIDs.append(((LUWCntr,)+(MdedID[0],),MdedID[1]))
 #   print(MdedIDs)
  #  print(MderIDs)
    if not MdedIDs:
        return []
    Binaries=[]
    for (MdedPoss,MdedID) in MdedIDs:
        MderPoss=next(MderID[0] for MderID in MderIDs if MderID[1]==MdedID)
        Binaries.append((MdedPoss,MderPoss,))
    Binaries=[(Poss[0][0],Poss[1][0]) for Poss in Binaries]
    Chains=myModule.Tree(Binaries).create_paths(NoInitTerms=True)
    FlatChains=[]
    for Chain in Chains:
        if len(Chain)==1:
            FlatChain=Chain[0]
        else:
            FlatChain=[]
            for Node in Chain:
                FlatChain.append(Node[0])
            FlatChain.append(Chain[-1][-1])
            FlatChain=tuple(FlatChain)
        FlatChains.append(FlatChain)
    return FlatChains

def get_next_suwfeats_withinds(LUW,FtNames):
    Fts=get_repeated_list((None,None),len(FtNames))
    for Cntr,SUW in enumerate(get_suws(LUW)):
        for (Ind,FtName) in enumerate(FtNames):
            if FtName in SUW.attrib.keys() and Fts[Ind] is (None,None):
                Fts[Ind]=(Cntr,SUW.attrib[FtName])
    return Fts

def get_repeated_list(El,Times):
    L=[]
    for i in range(Times):
        L.append(El)
    return L

def get_next_suwfeats(LUW,FtNames):
    Fts=get_repeated_list(None,len(FtNames))
    for SUW in get_suws(LUW):
        for (Ind,FtName) in enumerate(FtNames):
            if FtName in SUW.attrib.keys() and Fts[Ind] is None:
                Fts[Ind]=SUW.attrib[FtName]
    return Fts


def generate_grouped_luws(XmlFP,Unit='Sentence'):
    '''
    this is the main func, which returns the dict with sentence IDs as its keys and their corresponding LUWs as its values
    An LUW is an 'Element' object of ElementTree API of Python standard lib, and contains SUWs as its children, so that's all you'd need.
    Refer to https://docs.python.org/3/library/xml.etree.elementtree.html for details of this object
    '''
    assert(Unit in ['IPU','Sentence'])
    ETree=ET.parse(XmlFP)
    FndLUWs=[]
    InitNode=ETree.getroot()
    FndLUWs=[]
    LUWsPerUnit=[];PrvMderID=-float('inf')
    for IPU in return_immediate_targetnodes(InitNode,'IPU'):
        for LUW in return_immediate_targetnodes(IPU,'LUW'): 
            MderID,MdedID=[int(Ft) if Ft is not None else None for Ft in get_next_suwfeats(LUW,['Dep_BunsetsuUnitID','Dep_ModifieeBunsetsuUnitID'])]

            if MderID is not None:
                if MderID<PrvMderID:
                    yield FndLUWs
                    FndLUWs=[];PrvMderID=-float('inf')
                else:
                    PrvMderID=MderID
                    FndLUWs.append(LUW)
                    
            else:
                FndLUWs.append(LUW)


def return_immediate_targetnodes(ParentNode,TgtNodeName):
    Nodes=[]
    for ChildNode in ParentNode:
        if ChildNode.tag==TgtNodeName:
            Nodes.append(ChildNode)
    return Nodes


def find_nodes_in_tree(ParentNode,ResNodes=[],TgtNodes='all',ParentToo=True):
    assert TgtNodes=='all' or (isinstance(TgtNodes,list) and len(TgtNodes)==len(set(TgtNodes)))
    if TgtNodes=='all' or ParentNode.tag in TgtNodes:
        ResNodes.append((ParentNode,'root'))
    for ChildNode in ParentNode:
        if TgtNodes=='all' or ChildNode.tag in TgtNodes:
            FndEl=(ChildNode,ParentNode) if ParentToo else ChildNode
            ResNodes.append(FndEl)
            #TgtNodes.remove(ChildNode)
        Children=ChildNode.getchildren()
        if Children:
            ResNodes=find_nodes_in_tree(ChildNode,ResNodes=ResNodes,TgtNodes=TgtNodes)
#        elif any(TgtNode in [Child.tag for Child in Children] for TgtNode in TgtNodes):
#            sys.stderr.write('something funny')
            

    return ResNodes

def get_fps_withattrib(Dir,Attrib,TgtRegexes,MutualExclP=True):
    FndFPs={TgtRegex:[] for TgtRegex in TgtRegexes}
    for Cntr,FP in enumerate(glob.glob(Dir+'/*.xml')):
        SrcValue=get_attrib_fromfp(FP,Attrib)
        for Regex in TgtRegexes:
            CompiledRegex=re.compile(Regex)
            if re.match(CompiledRegex,SrcValue):
                FndFPs[Regex].append(FP)
                if MutualExclP:
                    break

    return FndFPs
        
def get_attrib_fromfp(FP,Attrib):
    InitNode=ET.parse(FP).getroot()
    Talk=InitNode
    AsVs=Talk.attrib
    if Attrib not in AsVs.keys():
        sys.exit('no such attrib: '+Attrib)
    return AsVs[Attrib]
            
        
        
        
def main():
    import argparse
    Psr=argparse.ArgumentParser()
    Psr.add_argument('input_dir')
    Psr.add_argument('attrib',choices=['SpeakerBirthGeneration','SpeakerBirthPlace','SpeakerSex'])
    Psr.add_argument('tgtvalue_regexes',nargs='+')
    Psr.add_argument('--output-fp')
    Psr.add_argument('--wanted-fts',nargs='+')

    Args=Psr.parse_args()

    FP=os.path.join(Args.input_dir,'-'.join(Args.tgtvalue_regexes)+'.pickle')
    ClassifiedFPs,_=myModule.ask_filenoexist_execute_pickle(FP,get_fps_withattrib,([Args.input_dir,Args.attrib,Args.tgtvalue_regexes],{}))
    for (Cat,FPs) in ClassifiedFPs.items():
        sys.stderr.write(Cat+': '+str(len(FPs))+' files\n')
        
    for Pair in itertools.combinations(Args.tgtvalue_regexes,2):
        Regex1,Regex2=Pair[0],Pair[1]
        FPs1,FPs2=ClassifiedFPs[Pair[0]],ClassifiedFPs[Pair[1]]
        Duplicates=set(FPs1).intersection(set(FPs2))
        if Duplicates:
            sys.stderr.out('there are duplicates between '+Regex1+' and '+Regex2+'\n')
    for Class,InFPs in ClassifiedFPs.items():
        print(Class)
        main0(InFPs)


if __name__ == '__main__':
    main()

