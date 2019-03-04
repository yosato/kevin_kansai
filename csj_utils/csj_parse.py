from xml.etree import ElementTree as ET
import os,sys,imp
from collections import defaultdict,OrderedDict
from pythonlib_ys import main as myModule

imp.reload(myModule)

def main0(XmlFP,WantedFts=[],Debug=False):
    ComplexNominals=[]
    for LUWsPerSent in generate_grouped_luws(XmlFP,Unit='Sentence'):
        print_orths_from_luws(LUWsPerSent)
        sys.stdout.write('--------------------\n')
        ChainsLUW=get_dependency_chains(LUWsPerSent)
        if Debug:
            for Chain in ChainsLUW:
                print_orths_from_luws(Chain)
        NominalLUWChains=get_complex_nominals(ChainsLUW)
        NominalLUWChains=group_chains(NominalLUWChains)
        for Chains in NominalLUWChains.values():
            if len(Chains)>=2:
                MaxChain=sorted(Chains,key=lambda x:len(x),reverse=True)[0]
                print_orths_from_luws([LUW[1] for LUW in Chain])
                sys.stdout.write('(')
                for Chain in Chains:
                 
                    print_orths_from_luws([LUW[1] for LUW in Chain],Delim=' ')
                sys.stdout.write(')\n')
            else:
                Chain=Chains[0]
                print_orths_from_luws([LUW[1] for LUW in Chain])

        ComplexNominals.append(NominalLUWChains)
        sys.stdout.write('========================\n')

def group_chains(Chains):
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
            #SUW=get_suws(LUW)[0]
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


def find_nodes_in_tree(ParentNode,ResNodes,TgtNodes='all',ParentToo=True):
    assert TgtNodes=='all' or (isinstance(TgtNodes,list) and len(TgtNodes)==len(set(TgtNodes)))
    
    for ChildNode in ParentNode:
        if TgtNodes=='all' or ChildNode.tag in TgtNodes:
            FndEl=(ChildNode,ParentNode) if ParentToo else ChildNode
            ResNodes.append(FndEl)
            #TgtNodes.remove(ChildNode)
        Children=ChildNode.getchildren()
        if Children:
            ResNodes=find_nodes_in_tree(ChildNode,ResNodes,TgtNodes=TgtNodes)
#        elif any(TgtNode in [Child.tag for Child in Children] for TgtNode in TgtNodes):
#            sys.stderr.write('something funny')
            

    return ResNodes
    
def main():
    import argparse
    Psr=argparse.ArgumentParser()
    Psr.add_argument('input_fp')
    Psr.add_argument('--output-fp')
    Psr.add_argument('--wanted-fts',nargs='+')

    Args=Psr.parse_args()
    if not Args.input_fp.endswith('.xml'):
        sys.exit('input file must end with xml extension')
    main0(Args.input_fp,WantedFts=Args.wanted_fts)


if __name__ == '__main__':
    main()

