from LBP import LBP
from SIAObject import user,business,review,CustomGraph,USER,PRODUCT
from datetime import datetime
import sys
import re
import networkx as nx
import matplotlib.pyplot as plt
import numpy
'''
@author: Sarath Rami
@author: Santhosh Kumar Manavasi Lakshminarayanan
'''

######################################################### Initializers
G=CustomGraph()
B = []
R = []
NR = []
node_colors = {}
edge_colors = {}
nodetoNodeLabelDict = {}
inputFileName = sys.argv[1]
userIdToDict = dict()
######################################################### METHODS
def createGrapth(G, inputFileName):
    with open(inputFileName) as f:
        for line in f:
            if re.match('^B=', line):
                exec(line)
                #print 'B = ', B
                bnss = business(B[0],B[1],B[2],B[4])
                G.add_node(bnss)
                #node_colors[bnss]='red'
            elif re.match('^R=', line):
                exec(line)
                #print 'R = ', R
                for recoRev in R:
                    revw = review(recoRev[0], recoRev[3], recoRev[2], B[0], recoRev[4], True)
                    usr = user(recoRev[1], recoRev[2])
                    dictUsr = userIdToDict.get(usr.getId())
                    if not dictUsr:
                        userIdToDict[usr.getId()] = usr
                        dictUsr = usr
                    G.add_node(dictUsr)
                    #node_colors[dictUsr] = 'blue'
                    #edge_colors[(bnss, dictUsr)] = 'green'
                    G.add_edge(bnss, dictUsr, dict({'review':revw}))
            elif re.match('^NR=', line):
                exec(line)
                #print 'NR = ', NR
                for noRecoRev in NR:
                    revw = review(noRecoRev[0], noRecoRev[3], noRecoRev[2], B[0], noRecoRev[4], False)
                    usr = user(noRecoRev[1], noRecoRev[2])
                    dictUsr = userIdToDict.get(usr.getId())
                    if not dictUsr:
                        userIdToDict[usr.getId()] = usr
                        dictUsr = usr
                    G.add_node(dictUsr)
                    #node_colors[dictUsr] = 'blue'
                    #edge_colors[bnss, dictUsr] = 'black'
                    G.add_edge(bnss, dictUsr, dict({'review':revw}))

def paintWithLabels(graph, nodecolor='red', edgecolor='blue'):
    nx.draw(graph,pos=nx.spring_layout(G), with_labels=False, node_color=nodecolor,edge_color=edgecolor, alpha=0.5, width=2.0)
    nx.draw_networkx_labels(graph, pos=nx.spring_layout(graph),labels=nodetoNodeLabelDict)
    plt.show()

def paint(nodecolor='red', edgecolor='blue'):
    nx.draw(G,pos=nx.spring_layout(G), with_labels=True, node_color=nodecolor,edge_color=edgecolor, alpha=0.5, width=2.0)
    plt.show()
    
################## MAIN #################################
#########################################################
beforeGraphPopulationTime = datetime.now()
createGrapth(G, inputFileName)
afterGraphPopulationTime = datetime.now()
beforeStatisticsGenerationTime = datetime.now()
for g in nx.connected_component_subgraphs(G):
    print g

#lenListComponent = [len(c.nodes()) for c in cc]
print'----------------------Number of Users, Businesses, Reviews----------------------------------------------------------------------'
#users = [node for node in G.nodes() if node.getNodeType() == USER]
#businesses = [node for node in G.nodes() if node.getNodeType() == PRODUCT]
#reviews = [edge for edge in G.edges()]
#print 'Number of Users- ',len(users),'Number of Businesses- ',len(businesses),'Number of Reviews- ',len(reviews)
#userDegreeDistribution = [len(G.neighbors(node)) for node in G.nodes() if node.getNodeType() == USER]
#businessDegreeDistribution = [len(G.neighbors(node)) for node in G.nodes() if node.getNodeType() == PRODUCT]
print'----------------------Component Sizes----------------------------------------------------------------------'
#print sorted(lenListComponent)
print'----------------------User to Neighbors Degree--------------------------------------------------------------'
#for node in G.nodes():
#    if node.getNodeType() == USER:
#        userToDegreeDict[node] = len(G.neighbors(node))
#    else:
#        businessToDegreeDict[node] = len(G.neighbors(node))

#for user in userToDegreeDict.keys():
#    print user.getId(),' ',userToDegreeDict[i]
#print userDegreeDistribution
print'----------------------Business to Neighbors Degree----------------------------------------------------------'
#for business in businessToDegreeDict.keys():
#    print business.getName(),' ',businessToDegreeDict[i]
#print businessDegreeDistribution
print '---------------------- Mean And Variance of the Distributions ----------------------------------------------------------'
#print 'Average Size Of a Component - ', numpy.mean(numpy.array(lenListComponent)),'Variance Of Component Size - ', numpy.var(numpy.array(lenListComponent)) 
#print 'Average Degree Of a User - ',numpy.mean(numpy.array(userDegreeDistribution)),'Variance Of User Degree - ', numpy.var(numpy.array(lenListComponent))
#print 'Average Degree Of a Business - ',numpy.mean(numpy.array(businessDegreeDistribution)),'Variance Of Business Degree - ', numpy.var(numpy.array(lenListComponent))
print'------------------------------------------------------------------------------------------------------------'
afterStatisticsGenerationTime = datetime.now()
##########################################################
beforeLBPRunTime = datetime.now()
#loopyBeliefPropagation = LBP(graph=G)
#loopyBeliefPropagation.doBeliefPropagation(False, 10)
afterLBPRunTime = datetime.now()
###########################################################
print'Graph Population time:', afterGraphPopulationTime-beforeGraphPopulationTime,
'Statistics Generation Time:', afterStatisticsGenerationTime-beforeStatisticsGenerationTime,
'Algo run Time:', afterLBPRunTime-beforeLBPRunTime
#nodetoNodeLabelDict = {node:node.getName() for node in G.nodes()}
#ncolors = [node_colors[x] for x in G.nodes()]
#paintWithLabels(ncolors,edge_colors.values())