"""
Simple demo with multiple subplots.



"""
import numpy as np
import matplotlib.pyplot as plt
from lshash import LSHash
from util import dataReader as dr, SIAUtil
import networkx


class SuperGraph(networkx.Graph):
    def __init__(self, parentUserIdToUserDict=dict(),parentBusinessIdToBusinessDict=dict(), parent_reviews= dict()):
        super(SuperGraph, self).__init__()
        self.userIdToUserDict = parentUserIdToUserDict
        self.businessIdToBusinessDict = parentBusinessIdToBusinessDict
        self.reviewIdToReviewDict = parent_reviews
    
    
    def addNodesAndEdge(self, usr, bnss, review):
        self.userIdToUserDict[usr.getId()] = usr
        self.businessIdToBusinessDict[bnss.getId()] = bnss
        self.reviewIdToReviewDict[review.getId()] = review
        super(SuperGraph, self).add_node((usr.getId(),SIAUtil.USER))
        super(SuperGraph, self).add_node((bnss.getId(),SIAUtil.PRODUCT))
        super(SuperGraph, self).add_edge((usr.getId(),SIAUtil.USER),\
                                              (bnss.getId(),SIAUtil.PRODUCT),\
                                               attr_dict={SIAUtil.REVIEW_EDGE_DICT_CONST: review.getId()})
    
    def getUser(self, userId):
        return self.userIdToUserDict[userId]
    
    def getBusiness(self, businessId):
        return self.businessIdToBusinessDict[businessId]
        
    def getReview(self,usrId, bnssId):
        return self.reviewIdToReviewDict[self.get_edge_data((usrId,SIAUtil.USER), (bnssId,SIAUtil.PRODUCT))[SIAUtil.REVIEW_EDGE_DICT_CONST]]
    
    @staticmethod
    def createGraph(usrIdToUserDict,bnssIdToBusinessDict, parent_reviews):
        graph = SuperGraph()
        for reviewKey in parent_reviews.iterkeys():
            review = parent_reviews[reviewKey]
            graph.addNodesAndEdge(usrIdToUserDict[review.getUserId()],\
                                         bnssIdToBusinessDict[review.getBusinessID()],\
                                         review)
        return graph
def checkPlot():
    x1 = [0, 1, 2, 3, 4, 5]
    y1 = [1, 1, 3, 4, 5, 1]
    plt.figure(figsize=(16, 18))
    for i in range(1, 10):
        ax = plt.subplot(len(range(1, 10)), 1, i)
        #plt.ylim((1,5))
        plt.yticks(range(1, 6))
        ax.grid('off')
        ax.plot(x1, y1, 'yo-')
        plt.title('A tale of 2 subplots')
        plt.ylabel('Damped oscillation' + str(i))
    plt.tight_layout()
    plt.show()    

def checklshash():
    lsh = LSHash(6, 8)
    lsh.index([1,2,3,4,5,6,7,8])
    lsh.index([2,3,4,5,6,7,8,9])
    lsh.index([10,12,99,1,5,31,2,3])
    print lsh.query([1,2,3,4,5,6,7,7])


def checkRestaurant():
    inputFileName = '/media/santhosh/Data/workspace/datalab/data/master.data'  
    (usrIdToUserDict,bnssIdToBusinessDict,reviewIdToReviewsDict) = dr.parseAndCreateObjects(inputFileName)
    #G = SuperGraph.createGraph(usrIdToUserDict,bnssIdToBusinessDict,reviewIdToReviewsDict)
    for bnssKey in bnssIdToBusinessDict:
        if bnssIdToBusinessDict[bnssKey].getName()=='Cheese Board Pizza':
            print bnssIdToBusinessDict[bnssKey].getUrl()

checkRestaurant()