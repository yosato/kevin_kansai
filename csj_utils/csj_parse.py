from xml.etree import ElementTree as ET
import os,sys
from collections import defaultdict,OrderedDict

def main0(XmlFP):
    SentsLUWs=get_luws(XmlFP,IPUMergeCnt=10)
    WantedFt='PlainOrthographicTranscription'
 #   Out=sys.stdout if OutFP is None else open(OutFP,'wt')
    for LUWsPerIPU in SentsLUWs.values():
        for LUW in LUWsPerIPU:
            SUWs=[Child for Child in LUW.getchildren() if Child.tag=='SUW']
            SUWsStr=' '.join([SUW.attrib[WantedFt] for SUW in SUWs])
            #if 'LUWPOS' in LUW.attrib.keys() and LUW.attrib['LUWPOS']=='名詞':
                
            
            
            sys.stdout.write(SUWsStr+'\n')
    #if OutFP:
     #   Out.close()

def get_luws(XmlFP,IPUMergeCnt=0):
    '''
    this is the main func, which returns the dict with sentence IDs as its keys and their corresponding LUWs as its values
    An LUW is an 'Element' object of ElementTree API of Python standard lib, and contains SUWs as its children, so that's all you'd need.
    Refer to https://docs.python.org/3/library/xml.etree.elementtree.html for details of this object
    '''
    ETree=ET.parse(XmlFP)
    FndLUWs=OrderedDict()
    InitNode=ETree.getroot()
    FndLUWs=OrderedDict()
    LUWsPerIPU=[];IPUIDs=[]
    for IPU in generate_nodes(InitNode,'IPU'):
        #LUWsPerIPU=[]
        IPUID=IPU.attrib['IPUID']
        Nodes=find_nodes_in_tree(IPU,[],TgtNodes=['LUW'],ParentToo=True)
        for (HitLUW,_) in Nodes:
            if 'LUWPOS' in HitLUW.attrib.keys() and HitLUW.attrib['LUWPOS']!='感動詞':
                LUWsPerIPU.append(HitLUW)
        if len(LUWsPerIPU)>=IPUMergeCnt:
            FndLUWs[tuple(IPUIDs+[IPUID])]=LUWsPerIPU
            LUWsPerIPU=[];IPUIDs=[]
        else:
            IPUIDs.append(IPUID)
    if IPUMergeCnt and LUWsPerIPU:
        FndLUWs[tuple(IPUIDs)]=LUWsPerIPU
    return FndLUWs

def generate_nodes(ParentNode,NodeName):
    for ChildNode in ParentNode:
        if ChildNode.tag==NodeName:
            yield ChildNode

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

    Args=Psr.parse_args()
    if not Args.input_fp.endswith('.xml'):
        sys.exit('input file must end with xml extension')
    main0(Args.input_fp)


if __name__ == '__main__':
    main()

