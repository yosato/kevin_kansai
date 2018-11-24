from xml.etree import ElementTree as ET
import os,sys,json
from collections import defaultdict

def main0(XmlFP,OutputFP,TgtNodes='all'):
    ETree=ET.parse(XmlFP)
    with open(OutputFP,'wt') as FSw:
        InitNode=ETree.getroot()
        Nodes=find_nodes_in_tree(InitNode,defaultdict(list),TgtNodes=TgtNodes)
        for (Node,Attrib) in Nodes:
            sys.stdout.write('\n'.join([Node,repr(Attrib)])+'\n\n')
            FSw.write(json.dumps([Node,Attrib])+'\n')

def find_nodes_in_tree(ParentNode,ResNodes,TgtNodes='all'):
    assert TgtNodes=='all' or (isinstance(TgtNodes,list) and len(TgtNodes)==len(set(TgtNodes)))
    
    for ChildNode in ParentNode:
        if TgtNodes=='all' or ChildNode.tag in TgtNodes:
            ResNodes[ChildNode.tag].append(ChildNode.attrib)
            #TgtNodes.remove(ChildNode)
        Children=ChildNode.getchildren()
        if all(TgtNode in [Child.tag for Child in Children] for TgtNode in TgtNodes):
            ResNodes=find_nodes_in_tree(ChildNode,ResNodes,TgtNodes=TgtNodes)
        elif any(TgtNode in [Child.tag for Child in Children] for TgtNode in TgtNodes):
            sys.stderr.write('something funny')
            

    return ResNodes
    
def main():
    import argparse
    Psr=argparse.ArgumentParser()
    Psr.add_argument('input_fp')
    Psr.add_argument('--output-fp')
    Psr.add_argument('--target-nodes',type=list,default=['LUW','SUW'])
    Args=Psr.parse_args()
    if not Args.input_fp.endswith('.xml'):
        sys.exit('input file must end with xml extension')
    if Args.output_fp is None:
        Args.output_fp=(''.join(Args.input_fp.split('.')[:-1]+['.parse']))
    main0(Args.input_fp,Args.output_fp,TgtNodes=Args.target_nodes)


if __name__ == '__main__':
    main()

