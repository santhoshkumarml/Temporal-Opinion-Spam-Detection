'''
Created on Nov 26, 2014

@author: Santhosh Kumar
'''
import dataReader
import SIAUtil

if __name__ == '__main__':
    (parentUserIdToUserDict,parentBusinessIdToBusinessDict,parent_reviews) = \
    dataReader.parseAndCreateObjects('E:\\sample_master.txt')
    
    cross_time_graphs = SIAUtil.createTimeBasedGraph(parentUserIdToUserDict,\
                                                          parentBusinessIdToBusinessDict,\
                                                           parent_reviews, '2-Y')
    
    parent_graph = SIAUtil.createGraph(parentUserIdToUserDict, parentBusinessIdToBusinessDict, parent_reviews) 
    
    cross_reviewids = dict()
    noOfEdges = 0
    for time_key in cross_time_graphs.iterkeys():
        for siaLink in cross_time_graphs[time_key].edges():
            noOfEdges+=1
            
    print len(parent_reviews),len(parent_graph.edges()),noOfEdges
#     out = set(parent_reviewIds.keys())-set(cross_reviewids.keys())
#     print 'review', len(out), [(parent_reviewIds[_id],_id) for _id in out]
    