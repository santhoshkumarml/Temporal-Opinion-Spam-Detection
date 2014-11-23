'''
@author: Santhosh Kumar Manavasi Lakshminaryanan
'''
from SIAUtil import PRODUCT, USER, REVIEW_EDGE_DICT_CONST
'''
 Loopy Belief Propagation
'''
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
    
    def getNeighborWithEdges(self, siaObject):
        return [(neighbor,self.graph.get_edge_data(siaObject, neighbor)) for neighbor in self.graph.neighbors(siaObject)] 
        
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
            (fakeUsers,honestUsers,badProducts,goodProducts,fakeReviews,realReviews) = self.calculateAndPrintBeliefVals()
            print 'fakeUsers:',len(fakeUsers),'honestUsers:',len(honestUsers), \
            'goodProducts:',len(goodProducts),'badProducts:',len(badProducts),\
            'fakeReviews:',len(fakeReviews),'realReviews:',len(realReviews)
            
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
        for siaObject in self.graph.nodes():
            beliefVal = siaObject.calculateBeliefVals();
            if siaObject.getNodeType() == USER:
                if(beliefVal[0] > beliefVal[1]):
                    fakeUsers.append(siaObject.getName()+' '+str(siaObject.getScore()))
                else:
                    honestUsers.append(siaObject.getName()+' '+str(siaObject.getScore()))
            else:
                if(beliefVal[0] > beliefVal[1]):
                    badProducts.append(siaObject.getName()+' '+str(siaObject.getScore())+' '+str(siaObject.getRating()))
                else:
                    goodProducts.append(siaObject.getName()+''+siaObject.getUrl()+' '+str(siaObject.getScore())+' '+str(siaObject.getRating()))
                    
                # last message from product to user represents a class probability for review
                (neighbor,edge) = self.getNeighborWithEdges(siaObject)
                messageToNeighbor = neighbor.getMessageFromNeighbor(siaObject)
                review = edge[REVIEW_EDGE_DICT_CONST]
                if(messageToNeighbor[0]>messageToNeighbor[1]):
                    fakeReviews.append(review)
                else:
                    realReviews.append(review)  
            
        return (fakeUsers,honestUsers,badProducts,goodProducts,fakeReviews,realReviews)