'''
@author: Santhosh Kumar Manavasi Lakshminaryanan
'''
from SIAUtil import PRODUCT, USER
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
            
            if not hasAnyMessageChanged:
                break
            
            if saturation>0:
                saturation-=1
            
                
            
    def calculateAndPrintBeliefVals(self):
        fakeUsers = []
        honestUsers = []
        goodProducts = []
        badProducts = []
        for siaObject in self.graph.nodes():
            siaObject.calculateBeliefVals();
            if siaObject.getNodeType() == USER:
                if(siaObject.getScore()[0] > siaObject.getScore()[1]):
                    fakeUsers.append(siaObject.getName()+' '+str(siaObject.getScore()))
                else:
                    honestUsers.append(siaObject.getName()+' '+str(siaObject.getScore()))
            else:
                if(siaObject.getScore()[0] > siaObject.getScore()[1]):
                    badProducts.append(siaObject.getName()+' '+str(siaObject.getScore())+' '+str(siaObject.getRating()))
                else:
                    goodProducts.append(siaObject.getName()+''+siaObject.getUrl()+' '+str(siaObject.getScore())+' '+str(siaObject.getRating()))

            #print siaObject.getAllMessageBuffer()
        
        print 'fakeUsers', fakeUsers
        print 'honestUsers', honestUsers
        print 'badProducts', badProducts
        print 'goodProducts', goodProducts