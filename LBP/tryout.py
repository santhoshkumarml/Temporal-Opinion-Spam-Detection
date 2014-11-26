'''
Created on Nov 26, 2014

@author: Santhosh Kumar
'''
import dataReader

if __name__ == '__main__':
    Years = []
    with open('E:\\workspace\\\dm\\data\\Temporal\\years.log') as f:
        for line in f:
            exec(line)
    year_sum = [sum(x) for x in Years]
    print year_sum
    final_sum = sum(year_sum)
    print final_sum
    (userIdToUserDict,businessIdToBusinessDict,reviews) =\
    dataReader.parseAndCreateObjects('E:\\sample_master.txt')
    print len(userIdToUserDict.keys())+len(businessIdToBusinessDict.keys())