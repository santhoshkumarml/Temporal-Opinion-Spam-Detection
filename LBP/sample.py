'''
Created on Nov 25, 2014

@author: Santhosh Kumar
'''
import SIAUtil
from SIAUtil import review
import dataReader

if __name__ == '__main__':
    (userIdToUserDict, \
     businessIdToBusinessDict,\
      reviews) = dataReader.parseAndCreateObjects('E:\\workspace\\\dm\\data\\crawl_old\\o_new_2.txt')
    graphs = SIAUtil.createTimeBasedGraph(userIdToUserDict, businessIdToBusinessDict, reviews, '1-M')
    print 'sample', graphs