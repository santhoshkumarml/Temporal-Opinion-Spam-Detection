from SIAUtil import user,business,review
import re
import networkx as nx
'''
@author: Sarath Rami
@author: Santhosh Kumar Manavasi Lakshminarayanan
'''
import SIAUtil

######################################################### Initializers
B = []
R = []
NR = []
node_colors = {}
edge_colors = {}
userIdToDict = dict()
######################################################### METHODS
def createGraph(inputFileName):
    G=nx.Graph()
    with open(inputFileName) as f:
        for line in f:
            if re.match('^B=', line):
                exec(line)
                #print 'B = ', B
                bnss = business(B[0],B[1],B[2],B[4])
                G.add_node(bnss)
                node_colors[bnss]='red'
            elif re.match('^R=', line):
                exec(line)
                #print 'R = ', R
                for recoRev in R:
                    #revw = review(recoRev[0], recoRev[3], recoRev[2], B[0], recoRev[4], True)
                    revw = review(recoRev[0], recoRev[3], recoRev[4], True)
                    usr = user(recoRev[1], recoRev[2])
                    dictUsr = userIdToDict.get(usr.getId())
                    if not dictUsr:
                        userIdToDict[usr.getId()] = usr
                        dictUsr = usr
                    G.add_node(dictUsr)
                    G.add_edge(bnss, dictUsr, dict({SIAUtil.EDGE_DICT_CONST:revw}))
                    node_colors[dictUsr] = 'blue'
                    edge_colors[(dictUsr,bnss)] = 'green'
            elif re.match('^NR=', line):
                exec(line)
                #print 'NR = ', NR
                for noRecoRev in NR:
                    #revw = review(noRecoRev[0], noRecoRev[3], noRecoRev[2], B[0], noRecoRev[4], False)
                    revw = review(noRecoRev[0], noRecoRev[3], noRecoRev[4], False)
                    usr = user(noRecoRev[1], noRecoRev[2])
                    dictUsr = userIdToDict.get(usr.getId())
                    if not dictUsr:
                        userIdToDict[usr.getId()] = usr
                        dictUsr = usr
                    G.add_node(dictUsr)
                    G.add_edge(bnss, dictUsr, dict({SIAUtil.EDGE_DICT_CONST:revw}))
                    node_colors[dictUsr] = 'blue'
                    edge_colors[(dictUsr,bnss)] = 'black'
    return G