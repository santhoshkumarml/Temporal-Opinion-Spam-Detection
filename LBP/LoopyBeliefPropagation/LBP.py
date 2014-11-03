'''
@author: Santhosh Kumar Manavasi Lakshminaryanan
'''
from LoopyBeliefPropagation.SIAObject import PRODUCT, USER
'''
 Loopy Belief Propagation
'''
class LBP(object):
    def __init__(self, customGraph):
        self.customGraph = customGraph
        
    def doBeliefPropagation(self, flipFromUsersToProducts, saturation):
        if saturation:
            if flipFromUsersToProducts:
                for user in self.customGraph.nodes():
                    if user.getNodeType() == USER:
                        user.calculateAndSendMessagesToNeighBors()
                self.doBeliefPropagation(not flipFromUsersToProducts, saturation)
            else:
                for product in self.customGraph.nodes():
                    if product.getNodeType() == PRODUCT:
                        product.calculateAndSendMessagesToNeighBors()
                self.doBeliefPropagation(not flipFromUsersToProducts, saturation-1)