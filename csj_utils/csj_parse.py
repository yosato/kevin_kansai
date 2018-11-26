from xml.etree import ElementTree as ET
import os,sys
from collections import defaultdict

def main0(XmlFP,OutFP=None):
    SentsLUWs=get_luws(XmlFP)
    WantedFt='PlainOrthographicTranscription'
    Out=sys.stdout if OutFP is None else open(OutFP,'wt')
    for LUWs in SentsLUWs.values():
        for LUW in LUWs:
            if 'LUWPOS' in LUW.attrib.keys() and LUW.attrib['LUWPOS']=='名詞':
                SUWs=[Child for Child in LUW.getchildren() if Child.tag=='SUW']
                SUWsStr=' '.join([SUW.attrib[WantedFt] for SUW in SUWs])
                sys.stdout.write(SUWsStr+'\n')
    if OutFP:
        Out.close()

def get_luws(XmlFP):
    '''
    this is the main func, which returns the dict with sentence IDs as its keys and their corresponding LUWs as its values
    An LUW is an 'Element' object of ElementTree API of Python standard lib, and contains SUWs as its children, so that's all you'd need.
    Refer to https://docs.python.org/3/library/xml.etree.elementtree.html for details of this object
    '''
    ETree=ET.parse(XmlFP)
    FndLUWs=defaultdict(list)
    InitNode=ETree.getroot()
    Nodes=find_nodes_in_tree(InitNode,[],TgtNodes=['LUW'],ParentToo=True)
    for (HitLUW,Parent) in Nodes:
        SentID=int(Parent.attrib['IPUID'])
        FndLUWs[SentID].append(HitLUW)

    return FndLUWs    


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
    main0(Args.input_fp,Args.output_fp)


if __name__ == '__main__':
    main()

