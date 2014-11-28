'''
Created on Nov 26, 2014

@author: Santhosh Kumar
'''
import dataReader
import SIAUtil
import numpy
import math

if __name__ == '__main__':
#     (parentUserIdToUserDict,parentBusinessIdToBusinessDict,parent_reviews) = \
#     dataReader.parseAndCreateObjects('E:\\sample_master.txt')
#     
#     cross_time_graphs = SIAUtil.createTimeBasedGraph(parentUserIdToUserDict,\
#                                                           parentBusinessIdToBusinessDict,\
#                                                            parent_reviews, '2-Y')
#     
#     parent_graph = SIAUtil.createGraph(parentUserIdToUserDict, parentBusinessIdToBusinessDict, parent_reviews) 
#     
#     cross_reviewids = dict()
#     noOfEdges = 0
#     for time_key in cross_time_graphs.iterkeys():
#         for siaLink in cross_time_graphs[time_key].edges():
#             noOfEdges+=1
#             
#     print len(parent_reviews),len(parent_graph.edges()),noOfEdges
#     out = set(parent_reviewIds.keys())-set(cross_reviewids.keys())
#     print 'review', len(out), [(parent_reviewIds[_id],_id) for _id in out]
    a1 = [0.5,0.499]
    values = [0.00069836322346220525,0.0010463929349825121,0.67]
    i = 0
    while i<len(values) :
         array = numpy.array([])
         mean = numpy.mean(array)
         std = numpy.std(array)
         v = values[i]
         print mean,std, mean-(3*std),mean+(3*std)
         if math.fabs(v-mean) > 3*std and std>0:
             print v
         else:
             a1.append(v)
         i+=1
    
    