'''
Created on Nov 17, 2014

@author: Santhosh Kumar
'''
##################VARIABLES#############################

from datetime import datetime
import numpy
import sys

from LBP import LBP
from SIAUtil import business, user
from dataReader import createGraph
import matplotlib.pyplot as plt
import networkx as nx
import SIAUtil


inputFileName = sys.argv[1]
RECOMMENDED_REVIEW_COLOR = 'black'
NOT_RECOMMENDED_REVIEW_COLOR = 'red'
USER_NODE_COLOR = 'green'
PRODUCT_NODE_COLOR = 'blue'
##################FUNCTIONS#############################
def paintWithLabels(graph,nodetoNodeLabelDict, nodecolor='red', edgecolor='blue'):
    nx.draw(graph,pos=nx.spring_layout(graph), with_labels=True,\
             node_color=nodecolor,edge_color=edgecolor, alpha=0.5, width=2.0,\
              labels=nodetoNodeLabelDict)
    plt.show()

def paint(graph, nodecolor='red', edgecolor='blue'):
    nx.draw(graph,pos=nx.spring_layout(graph), with_labels=True,\
             node_color=nodecolor,edge_color=edgecolor, alpha=1.0, width=10.0)
    plt.show()
################## MAIN #################################
#########################################################
beforeGraphPopulationTime = datetime.now()
G=createGraph(inputFileName)
afterGraphPopulationTime = datetime.now()
beforeStatisticsGenerationTime = datetime.now()
#for g in nx.connected_component_subgraphs(G):
#    print g
#cc = sorted(nx.connected_component_subgraphs(G,False), key=len)
#print'----------------------Number of Users, Businesses, Reviews----------------------------------------------------------------------'
users = [node for node in G.nodes() if node.getNodeType() == SIAUtil.USER]
businesses = [node for node in G.nodes() if node.getNodeType() == SIAUtil.PRODUCT]
reviews = [edge for edge in G.edges()]
print 'Number of Users- ', len(users), 'Number of Businesses- ', len(businesses),\
 'Number of Reviews- ', len(reviews)
# userDegreeDistribution = [len(G.neighbors(node)) for node in G.nodes() if node.getNodeType() == USER]
# businessDegreeDistribution = [len(G.neighbors(node)) for node in G.nodes() if node.getNodeType() == PRODUCT]
# print'----------------------Component Sizes----------------------------------------------------------------------'
#lenListComponents = [len(c.nodes()) for c in cc if len(c.nodes())>1 ]
#print lenListComponents
#print'----------------------User to Neighbors Degree--------------------------------------------------------------'
#for node in G.nodes():
#    if node.getNodeType() == USER:
#        userToDegreeDict[node] = len(G.neighbors(node))
#    else:
#        businessToDegreeDict[node] = len(G.neighbors(node))

#for user in userToDegreeDict.keys():
#    print user.getId(),' ',userToDegreeDict[i]
#print userDegreeDistribution
#print'----------------------Business to Neighbors Degree----------------------------------------------------------'
#for business in businessToDegreeDict.keys():
#    print business.getName(),' ',businessToDegreeDict[i]
#print businessDegreeDistribution
# print '---------------------- Mean And Variance of the Distributions ----------------------------------------------------------'
# print 'Average Size Of a Component - ', numpy.mean(numpy.array(lenListComponents)),'Variance Of Component Size - ', numpy.var(numpy.array(lenListComponents)) 
# print 'Average Degree Of a User - ',numpy.mean(numpy.array(userDegreeDistribution)),'Variance Of User Degree - ', numpy.var(numpy.array(userDegreeDistribution))
# print 'Average Degree Of a Business - ',numpy.mean(numpy.array(businessDegreeDistribution)),'Variance Of Business Degree - ', numpy.var(numpy.array(businessDegreeDistribution))
print'------------------------------------------------------------------------------------------------------------'
afterStatisticsGenerationTime = datetime.now()
##########################################################
beforeLBPRunTime = datetime.now()
lbp = LBP(graph=G)
lbp.doBeliefPropagationIterative(20)
(fakeUsers,honestUsers,badProducts,goodProducts,fakeReviews,realReviews) = \
 lbp.calculateAndPrintBeliefVals()
print 'fakeUsers=', len(fakeUsers)
print 'honestUsers=', len(honestUsers)
print 'goodProducts=', len(goodProducts)
print 'badProducts=', len(badProducts)
print 'fakeReviews=', len(fakeReviews)
print 'realReviews=', len(realReviews)
afterLBPRunTime = datetime.now()
###########################################################
print'Graph Population time:', afterGraphPopulationTime-beforeGraphPopulationTime,\
'Statistics Generation Time:', afterStatisticsGenerationTime-beforeStatisticsGenerationTime,\
'Algo run Time:', afterLBPRunTime-beforeLBPRunTime
# nodetoNodeLabelDict = {node:node.getName() for node in G.nodes()}
# ncolors = [USER_NODE_COLOR if x.getNodeType()==SIAUtil.USER else PRODUCT_NODE_COLOR for x in G.nodes()]
ecolors = [RECOMMENDED_REVIEW_COLOR \
             if G.get_edge_data(x1,x2)[SIAUtil.REVIEW_EDGE_DICT_CONST].isRecommended() \
              else NOT_RECOMMENDED_REVIEW_COLOR for (x1,x2) in G.edges()]
# paintWithLabels(G, nodetoNodeLabelDict, ncolors, ecolors)
