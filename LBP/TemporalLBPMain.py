'''
Created on Nov 25, 2014

@author: Santhosh Kumar
'''
import SIAUtil
import dataReader
from LBP import LBP
import numpy
from SIAUtil import TimeBasedGraph
from copy import deepcopy, copy
import os.path as p
import pickle

###################################################INITIALIZE_PREMILINARY_STEPS##########################################################
def initialize(inputFileName, file_path):
    cross_time_graphs = dict()
    parent_graph = object()
    if p.exists(file_path+'pickle1'):
        with open(file_path+'pickle1', 'rb') as f:
            cross_time_graphs = pickle.load(f)
         
    if p.exists(file_path+'pickle2'):
        with open(file_path+'pickle2', 'rb') as f:
            parent_graph = pickle.load(f)
            
    if(not isinstance(parent_graph, TimeBasedGraph)):
        (parentUserIdToUserDict, parentBusinessIdToBusinessDict, parent_reviews) =\
         dataReader.parseAndCreateObjects(inputFileName)
        parent_graph = SIAUtil.createGraph(parentUserIdToUserDict,parentBusinessIdToBusinessDict,parent_reviews)
        f = open(file_path+'pickle2', 'wb')
        try:
            pickle.dump(parent_graph, f)
        finally:
            f.close()
    
    if len(cross_time_graphs.keys()) == 0:
#     cross_9_months_graphs = SIAUtil.createTimeBasedGraph(parentUserIdToUserDict, parentBusinessIdToBusinessDict, parent_reviews, '9-M')
        cross_time_graphs = SIAUtil.createTimeBasedGraph(parentUserIdToUserDict, parentBusinessIdToBusinessDict, parent_reviews, '1-Y')
        f = open(file_path+'pickle1', 'wb')
        try:
            pickle.dump(cross_time_graphs, f)
        finally:
            f.close()
#
#    print 'Years:',[ [len(c.nodes())\
#                      for c in sorted(nx.connected_component_subgraphs(cross_time_graphs[time_key],False))]\
#                    for time_key in cross_time_graphs.iterkeys() ]

    for time_key in cross_time_graphs.iterkeys():
        print '----------------------------------GRAPH-', time_key, '---------------------------------------------'
        lbp = LBP(graph=cross_time_graphs[time_key])
        lbp.doBeliefPropagationIterative(10)
        fakeUsers, honestUsers, unclassifiedUsers, badProducts, goodProducts, unclassifiedProducts, fakeReviewEdges, realReviewEdges, unclassifiedReviewEdges = lbp.calculateBeliefVals()
        fakeReviews = [lbp.getEdgeDataForNodes(*edge) for edge in fakeReviewEdges]
        realReviews = [lbp.getEdgeDataForNodes(*edge) for edge in realReviewEdges]
        unclassifiedReviews = [lbp.getEdgeDataForNodes(*edge) for edge in unclassifiedReviewEdges]
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
        positiveReviewsInFakeReviews = [review for review in fakeReviews if 
            lbp.getEdgeDataForNodes(lbp.getUser(review.getUserId()), lbp.getBusiness(review.getBusinessID())).getReviewSentiment() == 
            SIAUtil.REVIEW_TYPE_POSITIVE]
        negativeReviewsInFakeReviews = [review for review in fakeReviews if 
            lbp.getEdgeDataForNodes(lbp.getUser(review.getUserId()), lbp.getBusiness(review.getBusinessID())).getReviewSentiment() == 
            SIAUtil.REVIEW_TYPE_NEGATIVE]
        realReviewsInFakeReviews = [review for review in fakeReviews if 
            lbp.getEdgeDataForNodes(lbp.getUser(review.getUserId()), lbp.getBusiness(review.getBusinessID())).isRecommended()]
        fakeReviewsInRealReviews = [review for review in realReviews if 
            not 
            lbp.getEdgeDataForNodes(lbp.getUser(review.getUserId()), lbp.getBusiness(review.getBusinessID())).isRecommended()]
        unclassifiedFakeReviews = [review for review in unclassifiedReviews if 
            not 
            lbp.getEdgeDataForNodes(lbp.getUser(review.getUserId()), lbp.getBusiness(review.getBusinessID())).isRecommended()]
        unclassifiedRealReviews = [review for review in unclassifiedReviews if 
            lbp.getEdgeDataForNodes(lbp.getUser(review.getUserId()), lbp.getBusiness(review.getBusinessID())).isRecommended()]
        print "Number of Positive Reviews in Fake Reviews", len(positiveReviewsInFakeReviews)
        print "Number of Negative Reviews in Fake Reviews", len(negativeReviewsInFakeReviews)
        print "Number of Real Reviews in Fake Reviews", len(realReviewsInFakeReviews)
        print "Number of Fake Reviews in Real Reviews", len(fakeReviewsInRealReviews)
        print "Number of Fake Reviews in Unclassified Reviews", len(unclassifiedFakeReviews)
        print "Number of Real Reviews in Unclassified Reviews", len(unclassifiedRealReviews)
    
    return (cross_time_graphs, parent_graph)

###################################################################DATASTRUCTURES################################################################################
def calculateCrossTimeDs(cross_time_graphs):
    bnss_score_all_time_map = dict()
    for time_key in cross_time_graphs.iterkeys():
        bnss_score_map_for_time = {bnss.getId():bnss.getScore() for bnss in cross_time_graphs[time_key].nodes() if bnss.getNodeType()==SIAUtil.PRODUCT}
        for bnss_key in bnss_score_map_for_time.iterkeys():
            if bnss_key not in bnss_score_all_time_map:
                bnss_score_all_time_map[bnss_key] = dict()
            time_score_map = bnss_score_all_time_map[bnss_key]
            time_score_map[time_key] = bnss_score_map_for_time[bnss_key]
    cross_time_business_id_set_dict = {time_key:set([bnss.getId() \
                                                     for bnss in cross_time_graphs[time_key].nodes()\
                                                      if bnss.getNodeType()==SIAUtil.PRODUCT])\
                                       for time_key in cross_time_graphs.iterkeys()}
    return (bnss_score_all_time_map,cross_time_business_id_set_dict)

################################################ALGO FOR MERGE###############################################################
def calculateVarianceMerge(cross_time_graphs, parent_graph):
    (bnss_score_all_time_map,cross_time_business_id_set_dict) = calculateCrossTimeDs(cross_time_graphs)
    
    # calculate interesting businesses across time
    mergeable_businessids = dict()
    not_mergeable_businessids = dict()
    for bnss_key in bnss_score_all_time_map.iterkeys():
        time_score_map = bnss_score_all_time_map[bnss_key]
        array = numpy.array([time_score_map[key][1] for key in time_score_map.iterkeys()])
        mean = numpy.mean(array)
        std = numpy.std(array)
        meanMinus3STD = mean - (2*std)
        meanPlus3STD = mean + (2*std)
        for time_key in time_score_map.iterkeys():
            good_product_score = time_score_map[time_key][1]
            if(meanMinus3STD<=good_product_score and good_product_score<=meanPlus3STD):
                if time_key not in mergeable_businessids:
                    mergeable_businessids[time_key] = set()
                mergeable_businessids[time_key].add(bnss_key)
            else:
                if time_key not in not_mergeable_businessids:
                    not_mergeable_businessids[time_key] = set()
                not_mergeable_businessids[time_key].add(bnss_key)
                
    # create a new super graph with all nodes
    alltimeD_access_merge_graph = TimeBasedGraph()
    all_time_userIdToUserDict = dict()
    all_time_bnssIdToBnssDict = dict()
    for time_key in cross_time_graphs.iterkeys():
        for siaObject in cross_time_graphs[time_key].nodes():
            if siaObject.getId() in all_time_userIdToUserDict or siaObject.getId() in all_time_bnssIdToBnssDict:
                continue
            newSiaObject = copy(siaObject)
            newSiaObject.reset()
            if(newSiaObject.getNodeType() == SIAUtil.USER):
                all_time_userIdToUserDict[newSiaObject.getId()] = newSiaObject
            else:
                all_time_bnssIdToBnssDict[newSiaObject.getId()] = newSiaObject
            alltimeD_access_merge_graph.add_node(newSiaObject)
    
    alltimeD_access_merge_graph.initialize(all_time_userIdToUserDict, all_time_bnssIdToBnssDict)
    
    # whatever businesses did not drastically change, get all the edges
    # of the business and add them to new super graph    
    for time_key in mergeable_businessids:
            graph = cross_time_graphs[time_key]
            for bnssid in mergeable_businessids[time_key]:
                bnss = graph.getBusiness(bnssid)
                usrs = graph.neighbors(bnss)
                for usr in usrs:
                    review = deepcopy(graph.get_edge_data(usr,bnss)[SIAUtil.REVIEW_EDGE_DICT_CONST])
                    alltimeD_access_merge_graph.add_edge(alltimeD_access_merge_graph.getBusiness(bnss.getId()),\
                                                         alltimeD_access_merge_graph.getUser(usr.getId()),\
                                                          {SIAUtil.REVIEW_EDGE_DICT_CONST:review})
                    graph.remove_edge(usr,bnss)

    # whatever businesses did drastically change,
    # we will copy the super graph and try adding these edges to the copied
    # graph and run LBP
    to_be_removed_edge_between_user_bnss = set()
    certifiedfFakes = set()
    for time_key in not_mergeable_businessids:
        copied_all_timeD_access_merge_graph =  deepcopy(alltimeD_access_merge_graph)
        graph = cross_time_graphs[time_key]
        for bnssid in mergeable_businessids[time_key]:
            bnss = graph.getBusiness(bnssid)
            usrs = graph.neighbors(bnss)
            for usr in usrs:
                review = deepcopy(graph.get_edge_data(usr,bnss)[SIAUtil.REVIEW_EDGE_DICT_CONST])
                copied_all_timeD_access_merge_graph.add_edge(copied_all_timeD_access_merge_graph.getBusiness(bnss.getId()),\
                                                             copied_all_timeD_access_merge_graph.getUser(usr.getId()),
                                                             {SIAUtil.REVIEW_EDGE_DICT_CONST:review})
        print "------------------------------------Running Merge LBP along with not mergeable ",time_key,"--------------------------------------"    
        copy_merge_lbp = LBP(copied_all_timeD_access_merge_graph)
        copy_merge_lbp.doBeliefPropagationIterative(20)
        (fakeUsers, honestUsers,unclassifiedUsers,\
          badProducts,goodProducts, unclassifiedProducts,\
          fakeReviewEdges, realReviewEdges,unclassifiedReviewEdges) = copy_merge_lbp.calculateBeliefVals()
        for edge in fakeReviewEdges:
            to_be_removed_edge_between_user_bnss.add((copy_merge_lbp.getEdgeDataForNodes(*edge).getUserId(),\
                                                       copy_merge_lbp.getEdgeDataForNodes(*edge).getBusinessID()))
            certifiedfFakes.add(copy_merge_lbp.getEdgeDataForNodes(*edge).getId())
    
    #from the drastically change businesses we have find out all fake edges in the above step
    # without them add rest of the edges to the super graph and run LBP on it
    for time_key in not_mergeable_businessids:
        graph = cross_time_graphs[time_key]
        for bnssid in mergeable_businessids[time_key]:
            bnss = graph.getBusiness(bnssid)
            usrs = graph.neighbors(bnss)
            for usr in usrs:
                if (usr.getId(),bnss.getId()) not in to_be_removed_edge_between_user_bnss:
                    review = deepcopy(graph.get_edge_data(usr,bnss)[SIAUtil.REVIEW_EDGE_DICT_CONST])
                    alltimeD_access_merge_graph.add_edge(alltimeD_access_merge_graph.getBusiness(bnss.getId()),\
                                                         alltimeD_access_merge_graph.getUser(usr.getId()),\
                                                          {SIAUtil.REVIEW_EDGE_DICT_CONST:review})
    print "------------------------------------Running Final Merge LBP--------------------------------------"
    merge_lbp = LBP(alltimeD_access_merge_graph)
    merge_lbp.doBeliefPropagationIterative(25)
    (fakeUsers, honestUsers,unclassifiedUsers,\
     badProducts,goodProducts, unclassifiedProducts,\
     fakeReviewEdges, realReviewEdges,unclassifiedReviewEdges) = merge_lbp.calculateBeliefVals()
    for edge in fakeReviewEdges:
        certifiedfFakes.add(merge_lbp.getEdgeDataForNodes(*edge).getId())
        to_be_removed_edge_between_user_bnss.add((merge_lbp.getEdgeDataForNodes(*edge).getUserId(),\
                                                    merge_lbp.getEdgeDataForNodes(*edge).getBusinessID())) 
    print "------------------------------------Running Parent LBP along with all Time Edges--------------------------------------"
    
    # run LBP on a non temporal full graph for comparison  
    parent_lbp = LBP(parent_graph)
    parent_lbp.doBeliefPropagationIterative(25)
    (parent_lbp_fakeUsers, parent_lbp_honestUsers,parent_lbp_unclassifiedUsers,\
          parent_lbp_badProducts, parent_lbp_goodProducts, parent_lbp_unclassifiedProducts,\
          parent_lbp_fakeReviewEdges, parent_lbp_realReviewEdges, parent_lbp_unclassifiedReviewEdges) = parent_lbp.calculateBeliefVals()

    print "-----------------------------------------------Statistics------------------------------------------------------------------"
    fakeReviewInParentLBP = set([parent_lbp.getEdgeDataForNodes(*edge).getId() for edge in parent_lbp_fakeReviewEdges]) 
    fakeReviewsFromYelp   = set([parent_lbp.getEdgeDataForNodes(*edge).getId() for edge in parent_graph.edges()\
                                  if not parent_lbp.getEdgeDataForNodes(*edge).isRecommended()] )
    fakeReviewsFromTemporalAlgo = certifiedfFakes
    #Accuracy
    print 'Temporal Algo',len(fakeReviewsFromTemporalAlgo)
    print 'LBP',len(fakeReviewInParentLBP)
    print 'Yelp', len(fakeReviewsFromYelp)
    print 'Intersection of Yelp with TemporalLBP', len(fakeReviewsFromYelp&fakeReviewsFromTemporalAlgo)
    print 'Intersection of Yelp with LBP', len(fakeReviewsFromYelp&fakeReviewInParentLBP)
    print 'Intersection of Temporal LBP with LBP', len(fakeReviewsFromTemporalAlgo&fakeReviewInParentLBP)
        
#############################################################################################################################


if __name__ == '__main__':
    inputFileName = 'E:\\workspace\\\dm\\data\\crawl_new\\sample_master.txt'
    file_path = "E:\\"
    (cross_time_graphs,parent_graph) = initialize(inputFileName, file_path)
    calculateVarianceMerge(cross_time_graphs, parent_graph)