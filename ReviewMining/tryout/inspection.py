import AppUtil
import os
from util import SIAUtil
from util import GraphUtil
from util.GraphUtil import SuperGraph

csvFolder = '/media/santhosh/Data/workspace/datalab/data/Itunes/'
plotDir = os.path.join(os.path.join(os.path.join(csvFolder, os.pardir), 'stats'), 'usr_stats')


def inspect():
    # Read data
    bnssIdToBusinessDict, reviewIdToReviewsDict, usrIdToUserDict = AppUtil.readData(csvFolder, readReviewsText=True)
    # Construct Graphs
    superGraph = SuperGraph.createGraph(usrIdToUserDict, \
                                        bnssIdToBusinessDict, \
                                        reviewIdToReviewsDict)
    # superGraph, cross_time_graphs = GraphUtil.createGraphs(usrIdToUserDict, \
    #                                     bnssIdToBusinessDict, \
    #                                     reviewIdToReviewsDict, timeLength='1-W')
    # for time_key in cross_time_graphs:
    #     print time_key, cross_time_graphs[time_key].getDateTime()
    usrKeys = [usr_key for usr_key, usr_type in superGraph.nodes() \
               if usr_type == SIAUtil.USER]
    for usr_key in usrKeys:
        usrStatFilePath = os.path.join(plotDir, usr_key+'.stats')
        with open(usrStatFilePath, 'w') as usrStatFile:
            usrStatFile.write('--------------------------------------------------------------------------------------------------------------------\n')
            usrStatFile.write('Statistics for User:'+usr_key+'\n')
            neighboring_bnss_nodes = superGraph.neighbors((usr_key, SIAUtil.USER))
            reviews_for_usr = [superGraph.getReview(usr_key, bnssId) for (bnssId, bnss_type) in neighboring_bnss_nodes]
            usrStatFile.write('Reviews for this usr:')
            usrStatFile.write('Number of reviews:'+str(len(neighboring_bnss_nodes)))
            usrStatFile.write('\n')
            reviews_sorted = sorted(reviews_for_usr, key=lambda key: SIAUtil.getDateForReview(key))
            for review in reviews_sorted:
                usrStatFile.write(review.toString())
                usrStatFile.write('\n')

inspect()