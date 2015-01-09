"""
Simple demo with multiple subplots.


"""
import numpy as np
import matplotlib.pyplot as plt
from lshash import LSHash
from util import dataReader as dr, SIAUtil
import networkx
from os.path import join
import json
from util.ScrappedDataReader import ScrappedDataReader


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
        
        if not super(SuperGraph, self).has_node((usr.getId(),SIAUtil.USER)):
            super(SuperGraph, self).add_node((usr.getId(),SIAUtil.USER))
        
        if not super(SuperGraph, self).has_node((bnss.getId(),SIAUtil.PRODUCT)):
            super(SuperGraph, self).add_node((bnss.getId(),SIAUtil.PRODUCT))
            
        if super(SuperGraph, self).has_edge((usr.getId(),SIAUtil.USER),\
                                              (bnss.getId(),SIAUtil.PRODUCT)):
            usrId = usr.getId()
            bnssId = bnss.getId()
            alreadyPresentReview =\
             self.reviewIdToReviewDict[self.get_edge_data(\
                                                          (usrId,SIAUtil.USER),\
                                                           (bnssId,SIAUtil.PRODUCT))[SIAUtil.REVIEW_EDGE_DICT_CONST]]
            if self.businessIdToBusinessDict[bnssId].getName() == 'Silver Rice':
                print alreadyPresentReview.getTimeOfReview(), self.userIdToUserDict[alreadyPresentReview.getUserId()].getName(), alreadyPresentReview.getBusinessID()
                print review.getTimeOfReview(), self.userIdToUserDict[review.getUserId()].getName(), review.getBusinessID()
                print alreadyPresentReview.getReviewText() == review.getReviewText(), review.getReviewText() 
        else:
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


    
def checkNewReader():
    #inputDirName = 'D:\\workspace\\datalab\\data\\NYC'
    #inputDirName = 'D:\\workspace\\datalab\\NYCYelpData2'
    #inputDirName = '/media/santhosh/Data/workspace/datalab/NYCYelpData2'
    inputDirName = '/media/santhosh/Data/workspace/datalab/data/from ubuntu/zips'
    #\\2 Duck Goose.txt
    #\\Cafe Habana.txt
    rdr = ScrappedDataReader()
    rdr.readData(inputDirName)    
    G = SuperGraph.createGraph(rdr.getUsrIdToUsrDict(), rdr.getBnssIdToBnssDict(), rdr.getReviewIdToReviewDict())
#     for bnssKey in rdr.getBnssIdToBnssDict():
#         if 'Halal Guys' in rdr.getBnssIdToBnssDict()[bnssKey].getName():
#             print rdr.getBnssIdToBnssDict()[bnssKey].getName(), len(G.neighbors((bnssKey,SIAUtil.PRODUCT)))
    usrKeys = [usrKey for usrKey in rdr.getUsrIdToUsrDict()]
    usrKeys = sorted(usrKeys, reverse=True, key = lambda x: len(G.neighbors((x,SIAUtil.USER))))
    
    for usrKey in usrKeys:
        neighbors = G.neighbors((usrKey,SIAUtil.USER))
        if len(neighbors) > 2 and len(neighbors)<10:
            allReviews = [G.getReview(usrKey, neighbor[0]) for neighbor in neighbors]
            rec_reviews = [r for r in allReviews if r.isRecommended()]
            not_rec_reviews = [r for r in allReviews if not r.isRecommended()]
            if len(rec_reviews)>0 and len(not_rec_reviews)>0:
                usr = rdr.getUsrIdToUsrDict()[usrKey]
                print usr.getName(),usr.getUsrExtra(), len(neighbors)
                for r in rec_reviews:
                    print 'Rec', r.getBusinessID(), r.getTimeOfReview()
                for r in not_rec_reviews:
                    print 'Not Rec', r.getBusinessID(), r.getTimeOfReview()
     
    
def doIndexForRestaurants():
    inputDirName = '/media/santhosh/Data/workspace/datalab/data/from ubuntu/zips'
    rdr = ScrappedDataReader()
    rdr.readData(inputDirName)
    result = dict()
    restaurants = []
    for bnssKey in rdr.getBnssIdToBnssDict():
        addr = bnssKey[1]
        bnss = rdr.getBnssIdToBnssDict()[bnssKey]
        outDict = dict()
        outDict['address'] = addr
        outDict['bnssName'] = bnss.getName()
        restaurants.append(outDict)
    result['bnss'] = restaurants
    with open(join(inputDirName, 'index.json'),'w') as f:
        json.dump(result, f)
         
        
checkNewReader()