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
#                       for c in sorted(nx.connected_component_subgraphs(cross_day_graphs[key],False))]\
#                     for key in cross_day_graphs.iterkeys() ]
#     print '15 Days:',[ [len(c.nodes())\
#                       for c in sorted(nx.connected_component_subgraphs(cross_15_days_graphs[key],False))]\
#                     for key in cross_15_days_graphs.iterkeys() ]
    
#     print 'Months:',[ [len(c.nodes())\
#                       for c in sorted(nx.connected_component_subgraphs(cross_month_graphs[key],False))]\
#                     for key in cross_month_graphs.iterkeys() ]
#     print '3 Months:',[ [len(c.nodes())\
#                       for c in sorted(nx.connected_component_subgraphs(cross_3_months_graphs[key],False))]\
#                     for key in cross_3_months_graphs.iterkeys() ]
#     print '6 Months:',[ [len(c.nodes())\
#                       for c in sorted(nx.connected_component_subgraphs(cross_6_months_graphs[key],False))]\
#                     for key in cross_6_months_graphs.iterkeys() ]
#     print '9 Months:',[ [len(c.nodes())\
#                       for c in sorted(nx.connected_component_subgraphs(cross_9_months_graphs[key],False))]\
#                     for key in cross_9_months_graphs.iterkeys() ]
#     
    print 'Years:',[ [len(c.nodes())\
                      for c in sorted(nx.connected_component_subgraphs(cross_year_graphs[key],False))]\
                    for key in cross_year_graphs.iterkeys() ]
    
    for key in cross_year_graphs.iterkeys():
        print '----------------------------------GRAPH-',key,'---------------------------------------------'
        lbp = LBP(graph=cross_year_graphs[key])
        lbp.doBeliefPropagationIterative(3)
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
        positiveReviewsInFakeReviews = [review for review in fakeReviews\
                              if lbp.getEdgeDataForNodes(review.getUserId(),\
                                                         review.getBusinessID()).getReviewSentiment() \
                                == SIAUtil.REVIEW_TYPE_POSITIVE]
        negativeReviewsInFakeReviews = [review for review in fakeReviews\
                              if lbp.getEdgeDataForNodes(review.getUserId(),\
                                                         review.getBusinessID()).getReviewSentiment() \
                                == SIAUtil.REVIEW_TYPE_NEGATIVE]
        realReviewsInFakeReviews = [review for review in fakeReviews\
                              if lbp.getEdgeDataForNodes(review.getUserId(),\
                                                         review.getBusinessID()).isRecommended()]
        fakeReviewsInRealReviews = [review for review in realReviews\
                              if not lbp.getEdgeDataForNodes(review.getUserId(),\
                                                             review.getBusinessID()).isRecommended()]
        unclassifiedFakeReviews = [review for review in unclassifiedReviews\
                              if not lbp.getEdgeDataForNodes(review.getUserId(),\
                                                             review.getBusinessID()).isRecommended()]
        unclassifiedRealReviews = [review for review in unclassifiedReviews\
                              if lbp.getEdgeDataForNodes(review.getUserId(),\
                                                         review.getBusinessID()).isRecommended()]
        print "Number of Positive Reviews in Fake Reviews",len(positiveReviewsInFakeReviews)
        print "Number of Negative Reviews in Fake Reviews",len(negativeReviewsInFakeReviews)
        print "Number of Real Reviews in Fake Reviews",len(realReviewsInFakeReviews)
        print "Number of Fake Reviews in Real Reviews",len(fakeReviewsInRealReviews)
        print "Number of Fake Reviews in Unclassified Reviews",len(unclassifiedFakeReviews)
        print "Number of Real Reviews in Unclassified Reviews",len(unclassifiedRealReviews)