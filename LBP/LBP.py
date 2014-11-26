'''
@author: Santhosh Kumar Manavasi Lakshminaryanan
'''
import SIAUtil
'''
 Loopy Belief Propagation
'''

from SIAUtil import PRODUCT, USER, REVIEW_EDGE_DICT_CONST


class LBP(object):
    def __init__(self, graph):
        self.graph = graph
#     def normalizeProductMessages(self):
#         for product in self.graph.nodes():
#             if product.getNodeType() == PRODUCT:
#                 product.normalizeMessages()
#     
#     def normalizeUserMessages(self):
#         for user in self.graph.nodes():
#             if user.getNodeType() == USER:
#                 user.normalizeMessages()
    def getUser(self, userId):
        user = self.graph.getUser(userId)
        return user
    
    def getBusiness(self,businessID):
        business = self.graph.getBusiness(businessID)
        return business
    
    def getEdgeDataForNodes(self,user,business):
        return self.graph.get_edge_data(user,business)[SIAUtil.REVIEW_EDGE_DICT_CONST]
    
    def getNeighborWithEdges(self, siaObject):
        return [(neighbor,self.graph.get_edge_data(siaObject, neighbor)) \
                for neighbor in self.graph.neighbors(siaObject)] 
        
    #DON't USE - will reach max recursion limit
    def doBeliefPropagationRecursive(self, limit):
        changedProducts = []
        changedUsers = []
        if not (limit==0):
            for user in self.graph.nodes():
                if user.getNodeType() == USER:
                    changedNodes = user.calculateAndSendMessagesToNeighBors(self.getNeighborWithEdges(user))
                    changedProducts.extend(changedNodes)
                    
            
            for product in self.graph.nodes():
                if product.getNodeType() == PRODUCT:
                    changedNodes = product.calculateAndSendMessagesToNeighBors(self.getNeighborWithEdges(product))
                    changedUsers.extend(changedNodes)
            noOfChangedProducts = len(changedProducts)
            noOfChangedUsers = len(changedUsers)
            totalNoOfChangedNodes = noOfChangedProducts+noOfChangedUsers
            if not (totalNoOfChangedNodes==0):
                self.doBeliefPropagation(limit-1)
                
    def doBeliefPropagationIterative(self, limit):
        while not (limit==0):
            changedProducts = []
            changedUsers = []
            for user in self.graph.nodes():
                if user.getNodeType() == USER:
                    changedNodes = user.calculateAndSendMessagesToNeighBors(self.getNeighborWithEdges(user))
                    changedProducts.extend(changedNodes)
            
            for product in self.graph.nodes():
                if product.getNodeType() == PRODUCT:
                    changedNodes = product.calculateAndSendMessagesToNeighBors(self.getNeighborWithEdges(product))
                    changedUsers.extend(changedNodes)
                    
            noOfChangedProducts = len(changedProducts)
            noOfChangedUsers = len(changedUsers)
            totalNoOfChangedNodes = noOfChangedProducts+noOfChangedUsers
            
            print 'changedNodes In This Iteration', totalNoOfChangedNodes 
            
            if (totalNoOfChangedNodes==0):
                break
            
            limit-=1
            
                
            
    def calculateBeliefVals(self):
        fakeUsers = []
        honestUsers = []
        goodProducts = []
        badProducts = []
        fakeReviews = []
        realReviews = []
        unclassifiedUsers = []
        unclassifiedProducts = []
        unclassifiedReviews = []
        
        for siaObject in self.graph.nodes():
            siaObject.calculateBeliefVals();
            beliefVal = siaObject.getScore()
            if siaObject.getNodeType() == USER:
                if(beliefVal[0] > beliefVal[1]):
                    fakeUsers.append(siaObject)
#                     fakeUsers.append(siaObject.getName()+' '+str(siaObject.getScore()))
                elif(beliefVal[0] == beliefVal[1]):
                    unclassifiedUsers.append(siaObject)
                else:
                    honestUsers.append(siaObject)
#                     honestUsers.append(siaObject.getName()+' '+str(siaObject.getScore()))
            else:
                if(beliefVal[0] > beliefVal[1]):
                    badProducts.append(siaObject)
#                     badProducts.append(siaObject.getName()+' '+siaObject.getUrl()+' '+\
#                                        str(siaObject.getScore())+' '+str(siaObject.getRating()))
                elif(beliefVal[0] == beliefVal[1]):
                    unclassifiedProducts.append(siaObject)
                else:
                    goodProducts.append(siaObject)
#                     goodProducts.append(siaObject.getName()+' '+siaObject.getUrl()+' '+\
#                                         str(siaObject.getScore())+' '+str(siaObject.getRating()))
                    
        for edge in self.graph.edges():
            review = self.graph.get_edge_data(*edge)[REVIEW_EDGE_DICT_CONST]
            review.calculateBeliefVals(*edge)
            beliefVal = review.getScore()
            if(beliefVal[0] > beliefVal[1]):
                fakeReviews.append(review)
#                 fakeReviews.append(review.getUser().getName()+\
#                                    ' '+review.getBusiness().getName()+\
#                                    ' '+str(messageFromProductToUser)+\
#                                    ' '+review.getRating()+ ' '+\
#                                    str(review.isRecommended()))
            elif(beliefVal[0] == beliefVal[1]):
                    unclassifiedReviews.append(review)
            else:
                realReviews.append(review)
#                 realReviews.append(review.getUser().getName()+\
#                                    ' '+review.getBusiness().getName()+\
#                                    ' '+str(messageFromProductToUser)+\
#                                    ' '+review.getRating()+ ' '+\
#                                    str(review.isRecommended()))  
#             
        return (fakeUsers,honestUsers,unclassifiedUsers,\
                badProducts,goodProducts,unclassifiedProducts,\
                fakeReviews,realReviews,unclassifiedReviews)