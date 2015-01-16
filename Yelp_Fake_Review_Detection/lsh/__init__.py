from util.ScrappedDataReader import ScrappedDataReader as sdr
from util.GraphUtil import TemporalGraph
from util import SIAUtil
import ShingleUtil
import sys
import numpy


def checkJacDocHash(inputDirName):
    scr = sdr()
    usrIdToUsrDict, bnssIdToBnssDict, reviewIdToReviewDict = scr.readData(inputDirName)
    cross_time_graphs = TemporalGraph.createTemporalGraph(usrIdToUsrDict, bnssIdToBnssDict, reviewIdToReviewDict, '2-M')
    for time_key in cross_time_graphs:
        G = cross_time_graphs[time_key]
        for bnss_node in G.nodes():
            bnss_key, bnss_type = bnss_node
            if bnss_type == SIAUtil.PRODUCT:
                reviewTextsInThisTimeBlock = [G.getReview(usr_key, bnss_key).getReviewText() for usr_key, usr_type in G.neighbors(bnss_node)]
                if len(reviewTextsInThisTimeBlock) > 1:
                    #print '------------------------------------------'
                    #print time_key, bnss_key
                    data_matrix = ShingleUtil.formDataMatrix(reviewTextsInThisTimeBlock)
                    candidateGroups = ShingleUtil.jac_doc_hash(data_matrix, 20, 50)
                    maxTextSimilarity = numpy.amax(numpy.bincount(candidateGroups))
                    print maxTextSimilarity
#                    sys.exit()
                    #print '------------------------------------------'

inputDirName = '/media/santhosh/Data/workspace/datalab/data/from ubuntu/main_zips'
inputDirName = 'D:\\workspace\\datalab\\data\\from ubuntu\\zips'
# texts = ['The food there is awesome. The server was ok.', 'The food there is awesome. jfnsdjnvjdsn. The server was ok. ']
# data = ShingleUtil.formDataMatrix(texts)
# print data
# print ShingleUtil.jac_doc_hash(data, 30, 5)
#ShingleUtil.s_curve()