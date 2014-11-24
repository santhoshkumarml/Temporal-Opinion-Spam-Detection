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
import dataReader
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
wholeGraph=dataReader.createGraph(inputFileName)
afterGraphPopulationTime = datetime.now()
beforeStatisticsGenerationTime = datetime.now()
print'----------------------Component Sizes----------------------------------------------------------------------'
cc = sorted(nx.connected_component_subgraphs(wholeGraph,False), key=len, reverse=True)
lenListComponents = [len(c.nodes()) for c in cc if len(c.nodes())>1 ]
print lenListComponents
G = cc[5]
print'----------------------Number of Users, Businesses, Reviews----------------------------------------------------------------------'
users = [node for node in G.nodes() if node.getNodeType() == SIAUtil.USER]
businesses = [node for node in G.nodes() if node.getNodeType() == SIAUtil.PRODUCT]
reviews = [edge for edge in G.edges()]
print 'Number of Users- ', len(users), 'Number of Businesses- ', len(businesses),\
 'Number of Reviews- ', len(reviews)

#print'----------------------User to Neighbors Degree--------------------------------------------------------------'
#for node in G.nodes():
#    if node.getNodeType() == USER:
#        userToDegreeDict[node] = len(G.neighbors(node))
#    else:
#        businessToDegreeDict[node] = len(G.neighbors(node))

#for user in userToDegreeDict.keys():
#    print user.getId(),' ',userToDegreeDict[i]

# userDegreeDistribution = [len(G.neighbors(node)) for node in G.nodes() if node.getNodeType() == SIAUtil.USER]
#print userDegreeDistribution
#print'----------------------Business to Neighbors Degree----------------------------------------------------------'
#for business in businessToDegreeDict.keys():
#    print business.getName(),' ',businessToDegreeDict[i]

# businessDegreeDistribution = [len(G.neighbors(node)) for node in G.nodes() if node.getNodeType() == SIAUtil.PRODUCT]
#print businessDegreeDistribution
# print '---------------------- Mean And Variance of the Distributions ----------------------------------------------------------'
# print 'Average Size Of a Component - ', numpy.mean(numpy.array(lenListComponents)),'Variance Of Component Size - ', numpy.var(numpy.array(lenListComponents)) 
# print 'Average Degree Of a User - ',numpy.mean(numpy.array(userDegreeDistribution)),'Variance Of User Degree - ', numpy.var(numpy.array(userDegreeDistribution))
# print 'Average Degree Of a Business - ',numpy.mean(numpy.array(businessDegreeDistribution)),'Variance Of Business Degree - ', numpy.var(numpy.array(businessDegreeDistribution))
print'------------------------------------------------------------------------------------------------------------'
afterStatisticsGenerationTime = datetime.now()
##########################################################
beforeLBPRunTime = datetime.now()
##################ALGO_START################
lbp = LBP(graph=G)
lbp.doBeliefPropagationIterative(10)
(fakeUsers,honestUsers,unclassifiedUsers,\
 badProducts,goodProducts,unclassifiedProducts,\
 fakeReviews,realReviews,unclassifiedReviews) = lbp.calculateAndPrintBeliefVals()
##################ALGO_END################ 
print 'positive reviews', len([lbp.getEdgeDataForNodes(*edge)\
                                for edge in G.edges()\
                              if lbp.getEdgeDataForNodes(*edge).getReviewSentiment()\
                               == SIAUtil.REVIEW_TYPE_POSITIVE])
print 'Negative reviews', len([lbp.getEdgeDataForNodes(*edge)\
                                for edge in G.edges()\
                              if lbp.getEdgeDataForNodes(*edge).getReviewSentiment()\
                               == SIAUtil.REVIEW_TYPE_NEGATIVE])
print 'honestUsers=', len(honestUsers)
print 'unclassfiedUsers=', len(unclassifiedUsers)
print 'goodProducts=', len(goodProducts)
print 'badProducts=', len(badProducts)
print 'unclassfiedProducts=', len(unclassifiedProducts)
print 'fakeReviews=', len(fakeReviews)
print 'realReviews=', len(realReviews)
print 'unclassfiedReviews=', len(unclassifiedReviews)
##################Accuracy calculation################# 
fakeReviewsRecommendation = [review for review in fakeReviews\
                              if lbp.getEdgeDataForNodes(review.getUser(),\
                                                         review.getBusiness()).isRecommended()]
realReviewsRecommendation = [review for review in realReviews\
                              if not lbp.getEdgeDataForNodes(review.getUser(),\
                                                             review.getBusiness()).isRecommended()]
unclassifiedRealReviews = [review for review in unclassifiedReviews\
                              if lbp.getEdgeDataForNodes(review.getUser(),\
                                                         review.getBusiness()).isRecommended()]
unclassifiedFakeReviews = [review for review in unclassifiedReviews\
                              if not lbp.getEdgeDataForNodes(review.getUser(),\
                                                             review.getBusiness()).isRecommended()]
print "Number of Real Reviews in Fake Reviews",len(fakeReviewsRecommendation)
print "Number of Fake Reviews in Real Reviews",len(realReviewsRecommendation)
print "Number of Fake Reviews in Unclassified Reviews",len(unclassifiedFakeReviews)
print "Number of Real Reviews in Unclassified Reviews",len(unclassifiedRealReviews)
afterLBPRunTime = datetime.now()
###########################################################
print'Graph Population time:', afterGraphPopulationTime-beforeGraphPopulationTime,\
'Statistics Generation Time:', afterStatisticsGenerationTime-beforeStatisticsGenerationTime,\
'Algo run Time:', afterLBPRunTime-beforeLBPRunTime
nodetoNodeLabelDict = {node:node.getName() for node in G.nodes()}
ncolors = [USER_NODE_COLOR if x.getNodeType()==SIAUtil.USER else PRODUCT_NODE_COLOR for x in G.nodes()]
ecolors = [RECOMMENDED_REVIEW_COLOR \
             if lbp.getEdgeDataForNodes(x1,x2).isRecommended() \
               else NOT_RECOMMENDED_REVIEW_COLOR for (x1,x2) in G.edges()]
paintWithLabels(G, nodetoNodeLabelDict, ncolors, ecolors)
