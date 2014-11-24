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
    def getEdgeDataForNodes(self,user,business):
        return self.graph.get_edge_data(user,business)[SIAUtil.REVIEW_EDGE_DICT_CONST]
    
    def getNeighborWithEdges(self, siaObject):
        return [(neighbor,self.graph.get_edge_data(siaObject, neighbor)) \
                for neighbor in self.graph.neighbors(siaObject)] 
        
    #DON't USE - will reach max recursion limit
    def doBeliefPropagationRecursive(self, saturation):
        hasAnyMessageChanged = False
        if saturation>0 or saturation<0:
            for user in self.graph.nodes():
                if user.getNodeType() == USER:
                    if user.calculateAndSendMessagesToNeighBors(self.getNeighborWithEdges(user)):
                        hasAnyMessageChanged = True
            
            for product in self.graph.nodes():
                if product.getNodeType() == PRODUCT:
                    if product.calculateAndSendMessagesToNeighBors(self.getNeighborWithEdges(product)):
                        hasAnyMessageChanged = True

            if hasAnyMessageChanged:
                self.doBeliefPropagation(saturation-1)
                
    def doBeliefPropagationIterative(self, saturation):
        while (saturation>0 or saturation<0):
            changedNodes=0
            hasAnyMessageChanged = False
            for user in self.graph.nodes():
                if user.getNodeType() == USER:
                    if user.calculateAndSendMessagesToNeighBors(self.getNeighborWithEdges(user)):
                        changedNodes += 1
                        hasAnyMessageChanged = True
            
            for product in self.graph.nodes():
                if product.getNodeType() == PRODUCT:
                    if product.calculateAndSendMessagesToNeighBors(self.getNeighborWithEdges(product)):
                        changedNodes += 1
                        hasAnyMessageChanged = True

            print 'changedNodes',changedNodes
            
            if not hasAnyMessageChanged:
                break
            
            if saturation>0:
                saturation-=1
            
                
            
    def calculateAndPrintBeliefVals(self):
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