'''
Created on Nov 25, 2014

@author: Santhosh Kumar
'''
import SIAUtil
import dataReader
import networkx as nx

if __name__ == '__main__':
    (userIdToUserDict, \
     businessIdToBusinessDict,\
      reviews) = dataReader.parseAndCreateObjects('E:\\workspace\\\dm\\data\\crawl_old\\sample_master.txt')
      
    cross_day_graphs = SIAUtil.createTimeBasedGraph(userIdToUserDict, businessIdToBusinessDict, reviews, '1-D')
    cross_15_days_graphs = SIAUtil.createTimeBasedGraph(userIdToUserDict, businessIdToBusinessDict, reviews, '15-D')
    
    cross_month_graphs = SIAUtil.createTimeBasedGraph(userIdToUserDict, businessIdToBusinessDict, reviews, '1-M')
    cross_3_months_graphs = SIAUtil.createTimeBasedGraph(userIdToUserDict, businessIdToBusinessDict, reviews, '3-M')
    cross_6_months_graphs = SIAUtil.createTimeBasedGraph(userIdToUserDict, businessIdToBusinessDict, reviews, '6-M')
    cross_9_months_graphs = SIAUtil.createTimeBasedGraph(userIdToUserDict, businessIdToBusinessDict, reviews, '9-M')
    
    cross_year_graphs = SIAUtil.createTimeBasedGraph(userIdToUserDict, businessIdToBusinessDict, reviews, '1-Y')
    
    print 'Days:',[ [len(c.nodes())\
                      for c in sorted(nx.connected_component_subgraphs(cross_day_graphs[key],False))]\
                    for key in cross_day_graphs.iterkeys() ]
    print '15 Days:',[ [len(c.nodes())\
                      for c in sorted(nx.connected_component_subgraphs(cross_15_days_graphs[key],False))]\
                    for key in cross_15_days_graphs.iterkeys() ]
    
    print 'Months:',[ [len(c.nodes())\
                      for c in sorted(nx.connected_component_subgraphs(cross_month_graphs[key],False))]\
                    for key in cross_month_graphs.iterkeys() ]
    print '3 Months:',[ [len(c.nodes())\
                      for c in sorted(nx.connected_component_subgraphs(cross_3_months_graphs[key],False))]\
                    for key in cross_3_months_graphs.iterkeys() ]
    print '6 Months:',[ [len(c.nodes())\
                      for c in sorted(nx.connected_component_subgraphs(cross_6_months_graphs[key],False))]\
                    for key in cross_6_months_graphs.iterkeys() ]
    print '9 Months:',[ [len(c.nodes())\
                      for c in sorted(nx.connected_component_subgraphs(cross_9_months_graphs[key],False))]\
                    for key in cross_9_months_graphs.iterkeys() ]
    
    print 'Years:',[ [len(c.nodes())\
                      for c in sorted(nx.connected_component_subgraphs(cross_year_graphs[key],False))]\
                    for key in cross_year_graphs.iterkeys() ]