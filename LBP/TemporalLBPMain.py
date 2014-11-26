'''
Created on Nov 25, 2014

@author: Santhosh Kumar
'''
import SIAUtil
import dataReader
import networkx as nx
from LBP import LBP

if __name__ == '__main__':
    (userIdToUserDict, \
     businessIdToBusinessDict,\
      reviews) = dataReader.parseAndCreateObjects('E:\\workspace\\\dm\\data\\crawl_old\\sample_master.txt')
      
#     cross_day_graphs = SIAUtil.createTimeBasedGraph(userIdToUserDict, businessIdToBusinessDict, reviews, '1-D')
#     cross_15_days_graphs = SIAUtil.createTimeBasedGraph(userIdToUserDict, businessIdToBusinessDict, reviews, '15-D')
    
#     cross_month_graphs = SIAUtil.createTimeBasedGraph(userIdToUserDict, businessIdToBusinessDict, reviews, '1-M')
#     cross_3_months_graphs = SIAUtil.createTimeBasedGraph(userIdToUserDict, businessIdToBusinessDict, reviews, '3-M')
#     cross_6_months_graphs = SIAUtil.createTimeBasedGraph(userIdToUserDict, businessIdToBusinessDict, reviews, '6-M')
#     cross_9_months_graphs = SIAUtil.createTimeBasedGraph(userIdToUserDict, businessIdToBusinessDict, reviews, '9-M')
    cross_year_graphs = SIAUtil.createTimeBasedGraph(userIdToUserDict, businessIdToBusinessDict, reviews, '1-Y')
    
#     print 'Days:',[ [len(c.nodes())\
#                       for c in sorted(nx.connected_component_subgraphs(cross_day_graphs[time_key],False))]\
#                     for time_key in cross_day_graphs.iterkeys() ]
#     print '15 Days:',[ [len(c.nodes())\
#                       for c in sorted(nx.connected_component_subgraphs(cross_15_days_graphs[time_key],False))]\
#                     for time_key in cross_15_days_graphs.iterkeys() ]
    
#     print 'Months:',[ [len(c.nodes())\
#                       for c in sorted(nx.connected_component_subgraphs(cross_month_graphs[time_key],False))]\
#                     for time_key in cross_month_graphs.iterkeys() ]
#     print '3 Months:',[ [len(c.nodes())\
#                       for c in sorted(nx.connected_component_subgraphs(cross_3_months_graphs[time_key],False))]\
#                     for time_key in cross_3_months_graphs.iterkeys() ]
#     print '6 Months:',[ [len(c.nodes())\
#                       for c in sorted(nx.connected_component_subgraphs(cross_6_months_graphs[time_key],False))]\
#                     for time_key in cross_6_months_graphs.iterkeys() ]
#     print '9 Months:',[ [len(c.nodes())\
#                       for c in sorted(nx.connected_component_subgraphs(cross_9_months_graphs[time_key],False))]\
#                     for time_key in cross_9_months_graphs.iterkeys() ]
#     
#    print 'Years:',[ [len(c.nodes())\
#                      for c in sorted(nx.connected_component_subgraphs(cross_year_graphs[time_key],False))]\
#                    for time_key in cross_year_graphs.iterkeys() ]
    
    for time_key in cross_year_graphs.iterkeys():
        print '----------------------------------GRAPH-',time_key,'---------------------------------------------'
        lbp = LBP(graph=cross_year_graphs[time_key])
        lbp.doBeliefPropagationIterative(10)
        (fakeUsers, honestUsers,unclassifiedUsers,\
          badProducts,goodProducts, unclassifiedProducts,\
          fakeReviews, realReviews,unclassifiedReviews) =lbp.calculateBeliefVals()
        print 'fakeUsers=', len(fakeUsers)
        print 'honestUsers=', len(honestUsers)
        print 'unclassfiedUsers=', len(unclassifiedUsers)
        print 'goodProducts=', len(goodProducts)
        print 'badProducts=', len(badProducts)
        print 'unclassfiedProducts=', len(unclassifiedProducts)
        print 'fakeReviews=', len(fakeReviews)
        print 'realReviews=', len(realReviews)
        print 'unclassfiedReviews=', len(unclassifiedReviews)
###########################################################Accuracy calculation######################################################################
        positiveReviewsInFakeReviews = [review for review in fakeReviews\
                                        if lbp.getEdgeDataForNodes(lbp.getUser(review.getUserId()),\
                                                         lbp.getBusiness(review.getBusinessID())).getReviewSentiment() \
                                        == SIAUtil.REVIEW_TYPE_POSITIVE]
        negativeReviewsInFakeReviews = [review for review in fakeReviews\
                                        if lbp.getEdgeDataForNodes(lbp.getUser(review.getUserId()),\
                                                         lbp.getBusiness(review.getBusinessID())).getReviewSentiment() \
                                        == SIAUtil.REVIEW_TYPE_NEGATIVE]
        realReviewsInFakeReviews = [review for review in fakeReviews\
                                    if lbp.getEdgeDataForNodes(lbp.getUser(review.getUserId()),\
                                                         lbp.getBusiness(review.getBusinessID())).isRecommended()]
        fakeReviewsInRealReviews = [review for review in realReviews\
                                    if not lbp.getEdgeDataForNodes(lbp.getUser(review.getUserId()),\
                                                         lbp.getBusiness(review.getBusinessID())).isRecommended()]
        unclassifiedFakeReviews = [review for review in unclassifiedReviews\
                                   if not lbp.getEdgeDataForNodes(lbp.getUser(review.getUserId()),\
                                                         lbp.getBusiness(review.getBusinessID())).isRecommended()]
        unclassifiedRealReviews = [review for review in unclassifiedReviews\
                                   if lbp.getEdgeDataForNodes(lbp.getUser(review.getUserId()),\
                                                         lbp.getBusiness(review.getBusinessID())).isRecommended()]
        print "Number of Positive Reviews in Fake Reviews",len(positiveReviewsInFakeReviews)
        print "Number of Negative Reviews in Fake Reviews",len(negativeReviewsInFakeReviews)
        print "Number of Real Reviews in Fake Reviews",len(realReviewsInFakeReviews)
        print "Number of Fake Reviews in Real Reviews",len(fakeReviewsInRealReviews)
        print "Number of Fake Reviews in Unclassified Reviews",len(unclassifiedFakeReviews)
        print "Number of Real Reviews in Unclassified Reviews",len(unclassifiedRealReviews)
###################################################################MERGE_GRAPHS################################################################################
bnss_score_cross_time_map = dict()
for time_key in cross_year_graphs.iterkeys():
    bnss_score_map_for_time = {bnss.getId():bnss.getScore() for bnss in cross_year_graphs[time_key].nodes() if bnss.getNodeType()==SIAUtil.PRODUCT}
    for bnss_key in bnss_score_map_for_time.iterkeys():
        if bnss_key in bnss_score_cross_time_map:
            bnss_score_cross_time_map[bnss_key] = dict()
        time_score_map = bnss_score_cross_time_map[bnss_key]
        time_score_map[time_key] = bnss_score_map_for_time[bnss_key]
print bnss_score_cross_time_map
        
