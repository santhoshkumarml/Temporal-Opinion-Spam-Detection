'''
Created on Nov 17, 2014

@author: Santhosh Kumar
'''
##################VARIABLES#############################

from datetime import datetime
import sys

import numpy
from LBP import LBP
from SIAUtil import USER, PRODUCT, business, user
from dataReader import createGraph, node_colors, edge_colors
import matplotlib.pyplot as plt
import networkx as nx


inputFileName = sys.argv[1]
#node_colors = {}
#edge_colors = {}
nodetoNodeLabelDict = {}
##################FUNCTIONS#############################
def paintWithLabels(graph,nodetoNodeLabelDict, nodecolor='red', edgecolor='blue'):
    nx.draw(graph,pos=nx.spring_layout(graph), with_labels=True,\
             node_color=nodecolor,edge_color=edgecolor, alpha=0.5, width=2.0, labels=nodetoNodeLabelDict)
    plt.show()

def paint(graph, nodecolor='red', edgecolor='blue'):
    nx.draw(graph,pos=nx.spring_layout(graph), with_labels=True, node_color=nodecolor,edge_color=edgecolor, alpha=1.0, width=10.0)
    plt.show()
################## MAIN #################################
#########################################################
beforeGraphPopulationTime = datetime.now()
G=createGraph(inputFileName)
afterGraphPopulationTime = datetime.now()
beforeStatisticsGenerationTime = datetime.now()
#for g in nx.connected_component_subgraphs(G):
#    print g
cc = sorted(nx.connected_component_subgraphs(G,False))
# print'----------------------Number of Users, Businesses, Reviews----------------------------------------------------------------------'
# users = [node for node in G.nodes() if node.getNodeType() == USER]
# businesses = [node for node in G.nodes() if node.getNodeType() == PRODUCT]
# reviews = [edge for edge in G.edges()]
# print 'Number of Users- ', len(users), 'Number of Businesses- ', len(businesses), 'Number of Reviews- ', len(reviews)
# userDegreeDistribution = [len(G.neighbors(node)) for node in G.nodes() if node.getNodeType() == USER]
# businessDegreeDistribution = [len(G.neighbors(node)) for node in G.nodes() if node.getNodeType() == PRODUCT]
# print'----------------------Component Sizes----------------------------------------------------------------------'
lenListComponents = [len(c.nodes()) for c in cc if len(c.nodes())>1 ]
print sorted(lenListComponents)
listComponents = sorted([c for c in cc if len(c.nodes())>1 ],reverse = True)
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
loopyBeliefPropagation = LBP(graph=G)
#loopyBeliefPropagation.doBeliefPropagationIterative(1000)
#loopyBeliefPropagation.calculateAndPrintBeliefVals()
afterLBPRunTime = datetime.now()
###########################################################
print'Graph Population time:', afterGraphPopulationTime-beforeGraphPopulationTime,\
'Statistics Generation Time:', afterStatisticsGenerationTime-beforeStatisticsGenerationTime,\
'Algo run Time:', afterLBPRunTime-beforeLBPRunTime
nodetoNodeLabelDict = {node:node.getName() for node in G.nodes()}
ncolors = [node_colors[x] for x in G.nodes()]
print len(G.edges()), G.edges()
print len(edge_colors.keys()), edge_colors.keys()
ecolors = [edge_colors[(x1,x2)] if type(x1)==user else edge_colors[(x2,x1)]  for (x1,x2) in G.edges()]
paintWithLabels(G, nodetoNodeLabelDict, ncolors, ecolors)
