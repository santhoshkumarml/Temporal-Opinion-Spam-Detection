from LoopyBeliefPropagation.LBP import *
from LoopyBeliefPropagation.SIAObject import *
__author__ = 'rami'

from math import *
import re
import networkx as nx
import matplotlib.pyplot as plt

######################################################### Initializers
G=CustomGraph()
B = []
R = []
NR = []
node_colors = {}
edge_colors = {}
nodetoNodeLabelDict = {}
######################################################### MAIN ()
def paint(nodecolor='red', edgecolor='blue'):
    nx.draw(G,pos=nx.spring_layout(G), with_labels=False, node_color=nodecolor,edge_color=edgecolor, alpha=0.5, width=2.0)
    nx.draw_networkx_labels(G, pos=nx.spring_layout(G),labels=nodetoNodeLabelDict)
    plt.show()

with open('../../../data/o_new_1.txt') as f:
    for line in f:
        if re.match('^B=', line):
            exec(line)
            print 'B = ', B
            bnss = business(B[0],B[1],B[2],B[4])
            G.add_node(bnss)
            node_colors[bnss]='red'
        elif re.match('^R=', line):
            exec(line)
            print 'R = ', R
            for recoRev in R:
                revw = review(recoRev[0], recoRev[3], recoRev[2], B[0], recoRev[4], True)
                usr = user(recoRev[1], recoRev[2])
                G.add_node(usr)
                node_colors[usr] = 'blue'
                edge_colors[(bnss, usr)] = 'green'
                G.add_edge(bnss, usr)
        elif re.match('^NR=', line):
            exec(line)
            print 'NR = ', NR
            for noRecoRev in NR:
                revw = review(noRecoRev[0], noRecoRev[3], noRecoRev[2], B[0], noRecoRev[4], False)
                usr = user(noRecoRev[1], noRecoRev[2])
                G.add_node(usr)
                node_colors[usr] = 'blue'
                edge_colors[bnss, usr] = 'black'
                G.add_edge(bnss, usr)

loopyBeliefPropagation = LBP(graph=G)
loopyBeliefPropagation.doBeliefPropagation(False, 10)
nodetoNodeLabelDict = {node:node.getName() for node in G.nodes()}
#ncolors = [node_colors[x] for x in G.nodes()]
#paint(ncolors,edge_colors.values())