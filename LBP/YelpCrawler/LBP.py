'''
@author: Santhosh Kumar Manavasi Lakshminaryanan
'''
from SIAObject import PRODUCT, USER
'''
 Loopy Belief Propagation
'''
class LBP(object):
    def __init__(self, graph):
        self.graph = graph
        
    def normalizeProductMessages(self):
        for product in self.graph.nodes():
            if product.getNodeType() == PRODUCT:
                product.normalizeMessages()
    
    def normalizeUserMessages(self):
        for user in self.graph.nodes():
            if user.getNodeType() == USER:
                user.normalizeMessages()
        
    def doBeliefPropagation(self, flipFromUsersToProducts, saturation):
        if saturation:
            if flipFromUsersToProducts:
                for user in self.graph.nodes():
                    if user.getNodeType() == USER:
                        user.calculateAndSendMessagesToNeighBors(self.graph.neighbors(user))
                self.normalizeProductMessages()
                self.doBeliefPropagation(not flipFromUsersToProducts, saturation)
            else:
                for product in self.graph.nodes():
                    if product.getNodeType() == PRODUCT:
                        product.calculateAndSendMessagesToNeighBors(self.graph.neighbors(product))
                self.normalizeUserMessages()
                self.doBeliefPropagation(not flipFromUsersToProducts, saturation-1)
        for siaObject in self.graph.nodes():
            siaObject.calculateBeliefVals();
            #print (siaObject.getName(),'---',siaObject.getScore())