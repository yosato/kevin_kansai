from xml.etree import ElementTree as ET
import os,sys
from collections import defaultdict,OrderedDict

def main0(XmlFP,WantedFts=[]):
    for LUWsPerUnit in generate_grouped_luws(XmlFP):
        for LUW in LUWsPerUnit:
            SUWs=get_suws(LUW)
            SUWsStr=' '.join([(SUW.attrib['Dep_BunsetsuUnitID'] if 'Dep_BunsetsuUnitID' in SUW.attrib.keys() else '')+' '+SUW.attrib['PlainOrthographicTranscription'] for SUW in SUWs])
            if WantedFts:
                FtsStr='\t'
                for (Ind,SUW) in enumerate(SUWs):
                    for WantedFt in WantedFts:
                        FtsStr+=' '+WantedFt+':'+SUW.attrib[WantedFt] if WantedFt in SUW.attrib.keys() else ''
            #if 'LUWPOS' in LUW.attrib.keys() and LUW.attrib['LUWPOS']=='名詞':
            sys.stdout.write(SUWsStr+FtsStr+'\n')
    #if OutFP:
     #   Out.close()

def get_repeated_list(El,Times):
    L=[]
    for i in range(Times):
        L.append(El)
    return L
def get_suws(LUW):
    return [Child.attrib['SUW'] for Child in LUW.get_children()]
def get_next_suwfeats(LUW,FtNames):
    Fts=get_repeated_list(None,len(FtNames))
    for SUW in LUW.get_suws(LUW):
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
    FndLUWs=OrderedDict()
    LUWsPerUnit=[];PrvUnitID=0
    for LUW in generate_nodes(InitNode,'LUW'):
        CurUnitID,CurModID=get_next_suwfeats(LUW,['Dep_BunsetsuUnitID','Dep_ModifieeBunsetsuUnitID'])
        if CurUnitID is not None:
            if CurUnitID<PrvUnitID:
                yield FndLUWs
        else:
            FndLUWs.append(LUW)

def generate_nodes(ParentNode,NodeName):
    for ChildNode in ParentNode:
        if ChildNode.tag==NodeName:
            yield ChildNode
        else:
            generate_nodes(ChildNode,NodeName)

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

