'''
Created on Feb 9, 2015

@author: santhosh
'''
# -*- coding: utf-8 -*-
from __future__ import division

import csv
from datetime import datetime
import json
from lshash import LSHash
import networkx
import numpy
import os
from os.path import join
import rpy2
import random
import sys

import cusum.cusum as cm
from itunes_utils.ItunesDataReader import ItunesDataReader
from lsh import ShingleUtil
import matplotlib.pyplot as plt
from temporal_statistics import measure_extractor
from util import SIAUtil, PlotUtil, GraphUtil
from util.GraphUtil import SuperGraph, TemporalGraph
from yelp_utils import dataReader as dr
from yelp_utils.YelpDataReader import YelpDataReader


def checkCusum():
    x = numpy.random.randn(300)/5
    x[100:200] += numpy.arange(0, 4, 4/100)
    ta, tai, taf, amp = cm.detect_cusum(x, 2, .02, True, True)
    print ta, tai, taf, amp
    
def checkCallRFromPy():
    x = numpy.random.randn(300)/5
    x[100:200] += numpy.arange(0, 4, 4/100)
    import rpy2.robjects as robjects
    from rpy2.robjects.packages import importr
    qcc = importr("qcc")
    data = robjects.vectors.FloatVector(x)
    q1 = qcc.cusum(data)
    print q1[-1]
    
def checkJacDocHash(inputDirName):
    scr = YelpDataReader()
    usrIdToUsrDict, bnssIdToBnssDict, reviewIdToReviewDict = scr.readData(inputDirName)
    cross_time_graphs = TemporalGraph.createTemporalGraph(usrIdToUsrDict, bnssIdToBnssDict, reviewIdToReviewDict, '2-M')
    for time_key in cross_time_graphs:
        G = cross_time_graphs[time_key]
        for bnss_node in G.nodes():
            bnss_key, bnss_type = bnss_node
            if bnss_type == SIAUtil.PRODUCT:
                reviewTextsInThisTimeBlock = [G.getReview(usr_key, bnss_key).getReviewText() for usr_key, usr_type in G.neighbors(bnss_node)]
                if len(reviewTextsInThisTimeBlock) > 1:
                    #print '------------------------------------------'
                    #print time_key, bnss_key
                    data_matrix = ShingleUtil.formDataMatrix(reviewTextsInThisTimeBlock)
                    candidateGroups = ShingleUtil.jac_doc_hash(data_matrix, 20, 50)
                    maxTextSimilarity = numpy.amax(numpy.bincount(candidateGroups))
                    print maxTextSimilarity
#                    sys.exit()
                    #print '------------------------------------------'

inputDirName = '/media/santhosh/Data/workspace/datalab/data/from ubuntu/main_zips'
inputDirName = 'D:\\workspace\\datalab\\data\\from ubuntu\\zips'
# texts = ['The food there is awesome. The server was ok.', 'The food there is awesome. jfnsdjnvjdsn. The server was ok. ']
# data = ShingleUtil.formDataMatrix(texts)
# print data
# print ShingleUtil.jac_doc_hash(data, 30, 5)
#ShingleUtil.s_curve()
def checkNonAscii():
    import codecs
    content = 'data='
    with open('/home/santhosh/out1.log',"r") as f:
        data = dict()
        content = content+f.readline()
        exec(content)
        line = data['ReviewComment']
        words = []
        for word in line.split():
            try :
                word = word.decode('unicode_escape').encode('ascii','ignore')
                words.append(word)
            except UnicodeDecodeError as ex:
                print word
                print ex
                words.append(word)
        print words
#         line = line.decode('utf-8')
#         line = line.replace('\\xc2\\xa0',' ')
#         line = line.replace(u'\xc0',' ')
#         line = line.replace(u'\xa0',' ')
#         line = str(line)
#         words = re.split('[ ]+', line)
        #print [word.replace('\xc2','') for word in line.split()]
#         line = line.decode('utf-8')
#         line = f.read()
        #print re.findall(u'xc2', line, flags=re.UNICODE)
#             line = line.replace(u'\\xc2',' ')
#             line = line.replace(u'\\xa0',' ')
#             line = line.replace(u'\xc2',' ')
#             line = line.replace(u'\xa0',' ')
#             line = str(line)
#             words =  re.split('[ ]+', line)
#             print words


# texts=['ok','Excellent!']
# texts = ['After going to Katz Deli to eat a $15 sandwich (and in the middle of eating it I might add), I suggested to my sister that we pack up our halves of uneaten sandwiches and make our way over to Pommes Frites to have a combination of pastrami sandwiches with double-fried fries with flavors of mayonnaise. We walked into this cute little fry "bar" around 11 pm and apparently we managed to beat the drunken lower east side crowd. With a shared regular size of fries it was plenty, but if you\'re feeling extra fiendish for some glorious mayo dipping action, maybe you should up the size and just walk home 20 blocks. We got the pesto mayo and roasted garlic mayo and just for future reference for anyone excited about awesome and tasty combinations, spreading some of the roasted garlic mayo on top of a pastrami sandwich is the SHIZZLE. Don\'t doubt, just trust. There aren\'t a lot of places to sit down and eat inside Pommes Frites but there are counter spaces with little holes to hold your cone of fries. If you do get to sit in one of the corner tables though it\'s a great little dark, pub-like atmosphere. Just take your choice of vinegar, ketchup, tabasco and all those delicious mayos and go on with your bad self. Twice fried and twice full I couldn\'t be happier.','Anything fried twice will automatically be the most disgustingly indulgent "snack" you can ever have. After going to Katz Deli to eat a $15 sandwich (and in the middle of eating it I might add), I gluttonously suggested to my brother that we pack up our halves of uneaten sandwiches and make our way over to Pommes Frites to have the ultimate combination of pastrami sandwiches with double-fried fries with flavors of mayonnaise never conceptualized by lowly California girls like myself. We walked into this cute little fry "bar" around 11 pm and apparently we managed to beat the drunken lower east side crowd. With a shared regular size of fries it was plenty, but if you\'re feeling extra fiendish for some glorious mayo dipping action, maybe you should up the size and just walk home 20 blocks. We got the pesto mayo and roasted garlic mayo and just for future reference for anyone excited about awesome and tasty combinations, spreading some of the roasted garlic mayo on top of a pastrami sandwich is the SHIZZLE. Don\'t doubt, just trust. There aren\'t a lot of places to sit down and eat inside Pommes Frites but there are counter spaces with little holes to hold your cone of fries. If you do get to sit in one of the corner tables though it\'s a great little dark, pub-like atmosphere. Just take your choice of vinegar, ketchup, tabasco and all those delicious mayos and go on with your bad self. Twice fried and twice full I couldn\'t be happier']
# print ShingleUtil.jac_doc_hash(ShingleUtil.formDataMatrix(texts),20,50)

def checkPlot():
    x1 = [0, 1, 2, 3, 4]
    y1 = [1, 1, 1, 1, 1]
    #plt.figure(figsize=(16, 18))
    plt.title('A tale of 2 subplots')
    plt.ylabel('Damped oscillation')
    plt.ylim(1,max(y1)+1)
    plt.plot(x1, y1)
#     for i in range(1, 10):
#         ax = plt.subplot(len(range(1, 10)), 1, i)
#         #plt.ylim((1,5))
#         plt.yticks(range(1, 6))
#         ax.grid('off')
#         ax.plot(x1, y1, 'yo-')
#         plt.title('A tale of 2 subplots')
#         plt.ylabel('Damped oscillation' + str(i))
#     plt.tight_layout()
    plt.show()
    
def checkPlot2():    
    fig = plt.figure()
    data = (0, 2, 3, 5, 5, 5, 9, 7, 8, 6, 6)
    ax = fig.add_subplot(1, 1, 1)
    ax.plot(data, 'r-', linewidth=4)
    ax.axvline(x=5, ymin=0, ymax=data[5] / max(data), linewidth=4)
    #ax.text(5, 4, 'your text here')
    plt.show()

def checklshash():
    lsh = LSHash(6, 8)
    lsh.index([1,2,3,4,5,6,7,8])
    lsh.index([2,3,4,5,6,7,8,9])
    lsh.index([10,12,99,1,5,31,2,3])
    print lsh.query([1,2,3,4,5,6,7,7])


def checkRestaurant():
    inputFileName = '/media/santhosh/Data/workspace/datalab/data/master.data'  
    (usrIdToUserDict,bnssIdToBusinessDict,reviewIdToReviewsDict) = dr.parseAndCreateObjects(inputFileName)
    #G = SuperGraph.createGraph(usrIdToUserDict,bnssIdToBusinessDict,reviewIdToReviewsDict)
    for bnssKey in bnssIdToBusinessDict:
        if bnssIdToBusinessDict[bnssKey].getName()=='Cheese Board Pizza':
            print bnssIdToBusinessDict[bnssKey].getUrl()


    
def checkNewReader():
    #inputDirName = 'D:\\workspace\\datalab\\data\\NYC'
    #inputDirName = 'D:\\workspace\\datalab\\NYCYelpData2'
    #inputDirName = '/media/santhosh/Data/workspace/datalab/NYCYelpData2'
    inputDirName = '/media/santhosh/Data/workspace/datalab/data/from ubuntu/zips'
    #\\2 Duck Goose.txt
    #\\Cafe Habana.txt
    rdr = YelpDataReader()
    rdr.readData(inputDirName)    
    G = SuperGraph.createGraph(rdr.getUsrIdToUsrDict(), rdr.getBnssIdToBnssDict(), rdr.getReviewIdToReviewDict())
    
    cc = sorted(networkx.connected_component_subgraphs(G, False), key=len, reverse=True)
    
    for g in cc:
        cbnssNodes = [node for node in g.nodes() if node[1] == SIAUtil.PRODUCT]
        for node in cbnssNodes:
            bnss = rdr.getBnssIdToBnssDict()[node[0]]
            print bnss.getId(), len(g.neighbors(node))
        print '-----------------------------------'
    
    bnssNodes = [node for node in G.nodes() if node[1] == SIAUtil.PRODUCT]
    bnssNodes = sorted(bnssNodes, reverse=True, key = lambda x: len(G.neighbors(x)))
    usrNodes = [node for node in G.nodes() if node[1] == SIAUtil.USER]
    usrNodes = sorted(usrNodes, reverse=True, key = lambda x: len(G.neighbors(x)))
    print len(bnssNodes), len(usrNodes)
    
    for bnssNode in bnssNodes:
        bnss = rdr.getBnssIdToBnssDict()[bnssNode[0]]
        print bnss.getName(), len(G.neighbors(bnssNode))
    
    print '=============================================================================='
    
    for usrNode in usrNodes:
        usr = rdr.getUsrIdToUsrDict()[usrNode[0]]
        print usr.getName(), usr.getUsrExtra(), len(G.neighbors(usrNode))
        
#     for bnssKey in rdr.getBnssIdToBnssDict():
#         if 'Halal Guys' in rdr.getBnssIdToBnssDict()[bnssKey].getName():
#             print rdr.getBnssIdToBnssDict()[bnssKey].getName(), len(G.neighbors((bnssKey,SIAUtil.PRODUCT)))
#     usrKeys = [usrKey for usrKey in rdr.getUsrIdToUsrDict()]
#     usrKeys = sorted(usrKeys, reverse=True, key = lambda x: len(G.neighbors((x,SIAUtil.USER))))
#     
#     for usrKey in usrKeys:
#         neighbors = G.neighbors((usrKey,SIAUtil.USER))
#         if len(neighbors) > 2 and len(neighbors)<10:
#             allReviews = [G.getReview(usrKey, neighbor[0]) for neighbor in neighbors]
#             rec_reviews = [r for r in allReviews if r.isRecommended()]
#             not_rec_reviews = [r for r in allReviews if not r.isRecommended()]
#             if len(rec_reviews)>0 and len(not_rec_reviews)>0:
#                 usr = rdr.getUsrIdToUsrDict()[usrKey]
#                 print usr.getName(),usr.getUsrExtra(), len(neighbors)
#                 for r in rec_reviews:
#                     print 'Rec', r.getBusinessID(), r.getTimeOfReview()
#                 for r in not_rec_reviews:
#                     print 'Not Rec', r.getBusinessID(), r.getTimeOfReview()
     
    
def doIndexForRestaurants():
    inputDirName = '/media/santhosh/Data/workspace/datalab/data/from ubuntu/zips'
    rdr = YelpDataReader()
    rdr.readData(inputDirName)
    result = dict()
    restaurants = []
    for bnssKey in rdr.getBnssIdToBnssDict():
        addr = bnssKey[1]
        bnss = rdr.getBnssIdToBnssDict()[bnssKey]
        outDict = dict()
        outDict['address'] = addr
        outDict['bnssName'] = bnss.getName()
        restaurants.append(outDict)
    result['bnss'] = restaurants
    with open(join(inputDirName, 'index.json'),'w') as f:
        json.dump(result, f)
         
        
def checkBucketTree():
    bucketTree = measure_extractor.constructIntervalTree(60)
    print bucketTree
    inputData = [1,4,4,4,8,16,32]
    for i in inputData:
        interval = measure_extractor.getBucketIntervalForBucketTree(bucketTree, i)
        begin,end,data = interval
        bucketTree.remove(interval)
        bucketTree[begin:end] = data+1.0
        
    print bucketTree
    
    rating_velocity_prob_dist = {(begin,end):(count_data/(6)) for (begin, end, count_data) in bucketTree}
    
    print rating_velocity_prob_dist
    
def checkYelpAPI():
    inputDirName = '/home/santhosh'
    rdr = YelpDataReader()
    rdr.readDataForBnss(inputDirName, 'Boho Cafe.txt')
    revws1 = rdr.getReviewIdToReviewDict().values()
    content = 'data='
    revws2 = []
    with open(join(inputDirName, 'bnss'), mode='r') as f:
        data = dict()
        content = content+f.readline()
        exec(content)
        revws2 = data['reviews']
    print len(revws1),len(revws2)

def checkUsersWithOnlyNotRecommendedReviews():
#     inputDirName = 'D:\\workspace\\datalab\\data\\z'
    inputDirName = '/media/santhosh/Data/workspace/datalab/data/z'
    rdr = YelpDataReader()
    rdr.readData(inputDirName)
    print 'Read Data'
    G = SuperGraph.createGraph(rdr.getUsrIdToUsrDict(), rdr.getBnssIdToBnssDict(), rdr.getReviewIdToReviewDict())
    print 'Graph Constructed'
    allUserIds = set([usrid for (usrid,usrtype) in G.nodes() if usrtype == SIAUtil.USER])
    usersWithAleastOneRecReviews = set()
    usersWithOnlyOneReview = set()
    for usrId in allUserIds:
        usr = rdr.getUsrIdToUsrDict()[usrId]
        usrExtra = usr.getUsrExtra()
        reviewCountString = usrExtra[1]
        reviewCountSplit = reviewCountString.split()
        reviewCount = int(reviewCountSplit[0])
        if reviewCount == 1:
            usersWithOnlyOneReview.add(usrId)

        bnss_nodes = G.neighbors((usrId,SIAUtil.USER))
        allReviews = [G.getReview(usrId, bnssId) for bnssId,bnssType in bnss_nodes]
        hasOneRecommended = False
        for revw in allReviews:
            if revw.isRecommended():
                hasOneRecommended = True
                break
        if hasOneRecommended:
            usersWithAleastOneRecReviews.add(usrId)
    
    usersWithNotRecommendedReviewsAlone = allUserIds-usersWithAleastOneRecReviews
    usersWithMultipleReviewsAndNotRecommendedReviewsAlone =\
     usersWithNotRecommendedReviewsAlone-usersWithOnlyOneReview
     
    print 'Total Users',len(allUserIds)
    print 'usersWithOnlyOneReview', len(usersWithOnlyOneReview)
    print 'usersWithAlteastOneRecReviews', len(usersWithAleastOneRecReviews)
    print 'usersWithNotRecommendedReviewsAlone', len(usersWithNotRecommendedReviewsAlone)  
    print 'usersWithMultipleNotRecReviewsAlone',len(usersWithMultipleReviewsAndNotRecommendedReviewsAlone)
        
def checkBnss():
#     inputDirName = 'D:\\workspace\\datalab\\data\\z'
    inputDirName = '/media/santhosh/Data/workspace/datalab/data/r'
    rdr = YelpDataReader()
    rdr.readData(inputDirName)
    print len(rdr.getBnssIdToBnssDict())

def plotDirCreation(inputFileName):
    import os
    inputDir =  join(join(join(inputFileName, os.pardir),os.pardir), 'latest')
    
    
def tryTemporalStatisticsForYelp():
    inputFileName = sys.argv[1]
    beforeDataReadTime = datetime.now()
    rdr = YelpDataReader()
    (usrIdToUserDict,bnssIdToBusinessDict,reviewIdToReviewsDict) = rdr.readData(inputFileName)
    
    afterDataReadTime = datetime.now()
    
    print 'TimeTaken for Reading data:',afterDataReadTime-beforeDataReadTime


def setMemUsage():
    import resource
    rsrc = resource.RLIMIT_DATA
    soft, hard = resource.getrlimit(rsrc)
    print 'Soft limit starts as  :', soft

    resource.setrlimit(rsrc, (4194304, hard)) #limit to one kilobyte

    soft, hard = resource.getrlimit(rsrc)
    print 'Soft limit changed to :', soft
    
        
def tryTemporalStatisticsForItunes():
    
    csvFolder = '/media/santhosh/Data/workspace/datalab/data/Itunes'
    rdr = ItunesDataReader()
    (usrIdToUserDict,bnssIdToBusinessDict,reviewIdToReviewsDict) = rdr.readData(csvFolder)
    
    timeLength = '1-M'
    
    superGraph,cross_time_graphs = GraphUtil.createGraphs(usrIdToUserDict,\
                                                           bnssIdToBusinessDict,\
                                                            reviewIdToReviewsDict, timeLength)

    plotDir =  join(join(csvFolder, os.pardir), 'latest')  
      
    bnssKeys = [bnss_key for bnss_key,bnss_type in superGraph.nodes()\
                 if bnss_type == SIAUtil.PRODUCT] 
    
    bnssKeys = sorted(bnssKeys, reverse=True, key = lambda x: len(superGraph.neighbors((x,SIAUtil.PRODUCT))))
    
    bnssKeySet = set(bnssKeys[:10])
    
    #bnssKeySet = set(['338464438','339532909'])

    bnss_statistics = measure_extractor.extractMeasures(usrIdToUserDict,bnssIdToBusinessDict,reviewIdToReviewsDict,\
                     superGraph, cross_time_graphs, plotDir, bnssKeySet)
    
    total_time_slots = len(cross_time_graphs.keys())
    
    PlotUtil.plotter(bnssKeySet, bnss_statistics, bnssIdToBusinessDict, total_time_slots, plotDir)
    
    
tryTemporalStatisticsForItunes()
