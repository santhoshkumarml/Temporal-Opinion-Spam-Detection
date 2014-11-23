'''
@author: Sarath Rami
@author: Santhosh Kumar Manavasi Lakshminarayanan
'''
######################################################### Initializers

import re

from SIAUtil import user, business, review, REVIEW_EDGE_DICT_CONST
import SIAUtil
import networkx as nx


B = []
R = []
NR = []
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
            elif re.match('^R=', line):
                exec(line)
                #print 'R = ', R
                for recoRev in R:
                    usr = user(recoRev[1], recoRev[2])
                    dictUsr = userIdToDict.get(usr.getId())
                    if not dictUsr:
                        userIdToDict[usr.getId()] = usr
                        dictUsr = usr
                    revw = review(recoRev[0], dictUsr, bnss, recoRev[3], recoRev[4], True)
                    #revw = review(recoRev[0], recoRev[3], recoRev[4], True)
                    G.add_node(dictUsr)
                    G.add_edge(bnss, dictUsr, dict({SIAUtil.REVIEW_EDGE_DICT_CONST:revw}))
            elif re.match('^NR=', line):
                exec(line)
                #print 'NR = ', NR
                for noRecoRev in NR:
                    usr = user(noRecoRev[1], noRecoRev[2])
                    dictUsr = userIdToDict.get(usr.getId())
                    if not dictUsr:
                        userIdToDict[usr.getId()] = usr
                        dictUsr = usr
                    revw = review(noRecoRev[0], dictUsr, bnss, noRecoRev[3], noRecoRev[4], False)
                    #revw = review(noRecoRev[0], noRecoRev[3], noRecoRev[4], False)
                    G.add_node(dictUsr)
                    G.add_edge(bnss, dictUsr, dict({SIAUtil.REVIEW_EDGE_DICT_CONST:revw}))
    return G