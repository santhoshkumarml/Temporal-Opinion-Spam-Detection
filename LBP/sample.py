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
    cross_day_graphs = SIAUtil.createTimeBasedGraph(userIdToUserDict, businessIdToBusinessDict, reviews, '1-M')
    cross_month_graphs = SIAUtil.createTimeBasedGraph(userIdToUserDict, businessIdToBusinessDict, reviews, '1-M')
    cross_year_graphs = SIAUtil.createTimeBasedGraph(userIdToUserDict, businessIdToBusinessDict, reviews, '1-M')
    print [len(c.nodes) for key in cross_day_graphs.iterkeys() for c in sorted(nx.connected_component_subgraphs(cross_day_graphs[key],False))]
    print [len(c.nodes) for key in cross_month_graphs.iterkeys() for c in sorted(nx.connected_component_subgraphs(cross_month_graphs[key],False))]
    print [len(c.nodes) for key in cross_year_graphs.iterkeys() for c in sorted(nx.connected_component_subgraphs(cross_year_graphs[key],False))]