from util.ScrappedDataReader import ScrappedDataReader as sdr
from util.GraphUtil import TemporalGraph
from util import SIAUtil
import ShingleUtil
import sys

inputDirName = '/media/santhosh/Data/workspace/datalab/data/from ubuntu/main_zips'
texts = ['abc def ghi jkl', 'bcd effg hijklm', 'abcde ehfgi klm', 'effgh ijklmnopqr','nop qrestv']
data = ShingleUtil.formDataMatrix(texts, 5)
print ShingleUtil.jac_doc_hash(data, 3, 3)
sys.exit()
scr = sdr()
(usrIdToUsrDict, bnssIdToBnssDict, reviewIdToReviewDict) = scr.readData(inputDirName)
cross_time_graphs = TemporalGraph.createTemporalGraph(usrIdToUsrDict, bnssIdToBnssDict, reviewIdToReviewDict, '2-M')
for time_key in cross_time_graphs:
    G = cross_time_graphs[time_key]
    for bnss_node in G.nodes():
        bnss_key, bnss_type = bnss_node
        if bnss_type == SIAUtil.PRODUCT:
            reviewTextsInThisTimeBlock = [G.getReview(usr_key,bnss_key).getReviewText()\
                                           for (usr_key, usr_type) in G.neighbors(bnss_node)]
            if len(reviewTextsInThisTimeBlock) > 1: 
                print time_key, bnss_key
                data_matrix = ShingleUtil.formDataMatrix(reviewTextsInThisTimeBlock, 5)
                #jac_doc_hash.jac_doc_hash(data_matrix, 10, 5)
                sys.exit()
                print '------------------------------------------'
