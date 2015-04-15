'''
Created on Feb 9, 2015

@author: santhosh
'''
# -*- coding: utf-8 -*-
from __future__ import division

import csv
from datetime import datetime, timedelta
import json
from lshash import LSHash
import networkx
import numpy
import os
from os.path import join
import rpy2
import random
import sys

import anomaly_detection.cusum as cm
from itunes_utils.ItunesDataReader import ItunesDataReader
from lsh import ShingleUtil
import matplotlib.pyplot as plt
from temporal_statistics import measure_extractor
from util import SIAUtil, PlotUtil, GraphUtil, StatConstants
from util.GraphUtil import SuperGraph, TemporalGraph
from yelp_utils import dataReader as dr
from yelp_utils.YelpDataReader import YelpDataReader
from anomaly_detection import AnomalyDetector
import changefinder
from scipy.signal import argrelextrema
import  math
from datetime import date

def checkGraphUtils():
    csvFolder = '/media/santhosh/Data/workspace/datalab/data/Itunes'
    rdr = ItunesDataReader()
    (usrIdToUserDict,bnssIdToBusinessDict,reviewIdToReviewsDict) = rdr.readData(csvFolder)

    timeLength = '1-M'
    superGraph,cross_time_graphs = GraphUtil.createGraphs(usrIdToUserDict, bnssIdToBusinessDict,\
                                                                    reviewIdToReviewsDict, timeLength)

def checkDataFrame():
    import rpy2.robjects as robjects
    from rpy2.robjects.packages import importr
    importr("AnomalyDetection")
    anomaly_detection = robjects.r['AnomalyDetectionTs']

    robjects.r('''
        rdateFn <- function(d , m, y) {
            dat <- paste(paste(toString(d),toString(m),sep="/"),toString(y), sep="/")
            return(dat)
        }
        ''')
    rdateFn = robjects.globalenv['rdateFn']
    dates = [date(2008, 7, 10), date(2008, 8, 9), date(2008, 9, 8),\
             date(2008, 10, 8), date(2008, 11, 7), date(2008, 12, 7),\
             date(2009, 1, 6), date(2009, 2, 5), date(2009, 3, 7),\
             date(2009, 4, 6), date(2009, 5, 6), date(2009, 6, 5),\
             date(2009, 7, 5), date(2009, 8, 4), date(2009, 9, 3),\
             date(2009, 10, 3), date(2009, 11, 2), date(2009, 12, 2),\
             date(2010, 1, 1), date(2010, 1, 31), date(2010, 3, 2),\
             date(2010, 4, 1), date(2010, 5, 1), date(2010, 5, 31),\
             date(2010, 6, 30), date(2010, 7, 30), date(2010, 8, 29),\
             date(2010, 9, 28), date(2010, 10, 28), date(2010, 11, 27),\
             date(2010, 12, 27), date(2011, 1, 26), date(2011, 2, 25),\
             date(2011, 3, 27), date(2011, 4, 26), date(2011, 5, 26),\
             date(2011, 6, 25), date(2011, 7, 25), date(2011, 8, 24),\
             date(2011, 9, 23), date(2011, 10, 23), date(2011, 11, 22),\
             date(2011, 12, 22), date(2012, 1, 21), date(2012, 2, 20),\
             date(2012, 3, 21), date(2012, 4, 20), date(2012, 5, 20),\
             date(2012, 6, 19), date(2012, 7, 19), date(2012, 8, 18),\
             date(2012, 9, 17), date(2012, 10, 17), date(2012, 11, 16),\
             date(2012, 12, 16), date(2013, 1, 15), date(2013, 2, 14),\
             date(2013, 3, 16), date(2013, 4, 15), date(2013, 5, 15),\
             date(2013, 6, 14), date(2013, 7, 14), date(2013, 8, 13),\
             date(2013, 9, 12), date(2013, 10, 12), date(2013, 11, 11),\
             date(2013, 12, 11), date(2014, 1, 10), date(2014, 2, 9),\
             date(2014, 3, 11), date(2014, 4, 10), date(2014, 5, 10),\
             date(2014, 6, 9), date(2014, 7, 9), date(2014, 8, 8),\
             date(2014, 9, 7), date(2014, 10, 7), date(2014, 11, 6),\
             date(2014, 12, 6), date(2015, 1, 5), date(2015, 2, 4),\
             date(2015, 3, 6), date(2015, 4, 5)]

    dates = [datetime.combine(dates[i], datetime.min.time()) for i in range(len(dates))]
    values = [161,109,86,25,102,223,241,228,239,188,142,113,142,133,101,
            84,83,244,945,192,208,186,107,144,238,149,88,111,93,132,
            118,101,123,617,5501,1756,1373,513,2909,1256,2200,2434,2860,240,1938,
            2062,158,0,0,0,0,0,0,0,0,0,0,0,0,0,
            0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
            0,0,0,0,0,0,1,0]

    date_value_dict = {'a':robjects.POSIXct(dates), 'b':robjects.IntVector(values)}
    dataf = robjects.DataFrame(date_value_dict)
    res = anomaly_detection(dataf, plot= True)
    anoms_data_f = res[res.names.index('anoms')]
    anoms_dates = set()
    for d in anoms_data_f.rx2(1):
        anoms_dates.add(datetime.fromtimestamp(d).date())
    idxs = []
    dates = [dates[i].date() for i in range(len(dates))]
    for i in range(len(dates)):
        if dates[i] in anoms_dates:
            idxs.append(i)
    print idxs
    values = numpy.atleast_1d(values).astype('int64')
    fig = plt.figure()
    ax1 = fig.add_subplot(1, 1, 1)
    ax1.plot(values)
    ax1.plot(idxs, values[idxs], 'o', mfc='r', mec='r', mew=1, ms=5,
             label='Alarm')
    plt.show()

def checkR():
    import rpy2.robjects as robjects
    from rpy2.robjects.packages import importr
    data=[3.32919255,3.64074074,3.84269663,3.90813648,4.00207039,4.12747875
            ,4.17529039,4.2212766,4.24964639,4.22222222,4.22419725,4.2175552
            ,4.23211606,4.24624765,4.25167936,4.25248166,4.2575,4.25680787
            ,4.29813318,4.30547474,4.29731762,4.29461078,4.28444652,4.26276548
            ,4.24914237,4.23062539,4.20832483,4.15762171,4.13535749,4.0970021
            ,4.06199813,4.03958944,4.0111131,4.07295029,4.46319569,4.50791645
            ,4.5365574,4.53393311,4.58877685,4.59767227,4.57510136,4.58629547
            ,4.59982221,4.60221015,4.61307239,4.62219092,4.62106638,4.62106638
            ,4.62106638,4.62106638,4.62106638,4.62106638,4.62106638,4.62106638
            ,4.62106638,4.62106638,4.62106638,4.62106638,4.62106638,4.62106638
            ,4.62106638,4.62106638,4.62106638,4.62106638,4.62106638,4.62106638
            ,4.62106638,4.62106638,4.62106638,4.62106638,4.62106638,4.62106638
            ,4.62106638,4.62106638,4.62106638,4.62106638,4.62106638,4.62106638
            ,4.62106638,4.62106638,4.62106638,4.62105966,4.62105966]
    x = numpy.atleast_1d(data).astype('float64')
    data = numpy.atleast_1d(data).astype('float64')
    qcc = importr("qcc")
    data = robjects.vectors.FloatVector(data)
    robjects.r('''
            cusum_run <- function(data) {
            	idx <- 1
	            changes <- c()
	            index <- 1
	            for (i in 2:length(data))
	            {
		            out <- cusum(data[idx:i-1], se.shift=0.5, newdata=data[i], plot=FALSE)
		            if(length(out$violations$upper)>0) {
		            if (i-idx %in% out$violations$upper) {
	 		            idx = i
			            changes[index] = idx
			            index <- index+1
		            }
		            } else if(length(out$violations$lower)>0) {
		                if (i-idx %in% out$violations$lower) {
    		            idx=i
			            changes[index] = idx
			            index <- index+1
		            }
		            }
	            }
	            return (changes)
                }
            ''')
    cusum_run = robjects.globalenv['cusum_run']
    changes = cusum_run(data)
    changes = list([v-1 for k,v in changes.items()])
    print x
    plotCusumChanges(changes, x)

def testCFForSomeMeasures():
    data = []
    # number of reviews - cumulative
    data1 = [32.,    58.,    66.,\
            71.,    73.,    83.,   110.,   119.,   125.,   129.,   146.,\
            158.,   166.,   172.,   185.,   191.,   208.,   232.,   272.,\
            307.,   352.,   371.,   442.,   482.,   560.,   657.,   700.,\
            738.,   764.,   780.,   805.,   852.,   897.,   919.,   955.,\
            1035.,  1066.,  1157.,  1210.,  1629.,  2046.,  2893.,  3010.,\
            3999.,  4585.,  5182.,  5182.,  5182.,  5182.,  5182.,  5182.,\
            5182.,  5182.,  5182.,  5182.,  5182.,  5182.,  5182.,  5182.,\
            5182.,  5182.,  5182.,  5182.,  5182.,  5182.,  5182.,  5182.,\
            5182.,  5182.,  5182.,  5182.,  5182.,  5182.,  5182.,  5182.,\
            5182.,  5182.,  5182.,  5182.,  5182.,  5182.,  5182.,  5182.]

    # number of reviews - non cumulative
    data_1 = [32.0, 26.0, 8.0,\
              5.0, 2.0, 10.0, 27.0, 9.0, 6.0, 4.0, 17.0,\
              12.0, 8.0, 6.0, 13.0, 6.0, 17.0, 24.0, 40.0,\
              35.0, 45.0, 19.0, 71.0, 40.0, 78.0, 97.0, 43.0,\
              38.0, 26.0, 16.0, 25.0, 47.0, 45.0, 22.0, 36.0, 80.0,\
              31.0, 91.0, 53.0, 419.0, 417.0, 847.0, 117.0, 989.0, 586.0,\
              597.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,\
              0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,\
              0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,\
              0.0, 0.0, 0.0, 0.0]

    data.append(data1)

    # rating entropy
    data2 = [1.98426583,\
        2.15029501,  1.06127812,  1.52192809,  1.        ,  2.04643934,\
        2.09512685,  1.65774273,  1.45914792,  0.81127812,  2.2066294 ,\
        1.04085208,  1.40563906,  1.79248125,  1.91434118,  1.45914792,\
        2.06355861,  1.95914792,  1.9507006 ,  2.03674971,  2.06454172,\
        2.23399791,  2.16598914,  2.29918146,  2.07008564,  2.1730492 ,\
        2.1085896 ,  1.88740944,  2.13393757,  1.74899922,  2.22863457,\
        1.90942922,  1.93472066,  2.18670435,  1.72957396,  1.94059146,\
        1.48771125,  2.21787176,  2.20576684,  1.17457661,  1.14170929,\
        1.05168061,  1.32912829,  1.04355444,  1.05763042,  0.97630203,\
        0.97630203,  0.97630203,  0.97630203,  0.97630203,  0.97630203,\
        0.97630203,  0.97630203,  0.97630203,  0.97630203,  0.97630203,\
        0.97630203,  0.97630203,  0.97630203,  0.97630203,  0.97630203,\
        0.97630203,  0.97630203,  0.97630203,  0.97630203,  0.97630203,\
        0.97630203,  0.97630203,  0.97630203,  0.97630203,  0.97630203,\
        0.97630203,  0.97630203,  0.97630203,  0.97630203,  0.97630203,\
        0.97630203,  0.97630203,  0.97630203,  0.97630203,  0.97630203,\
        0.97630203,  0.97630203]
    data.append(data2)

    #Avg rating
    data3 = [3.84375   ,\
        3.70689655,  3.77272727,  3.73239437,  3.71232877,  3.71084337,\
        3.71818182,  3.7394958 ,  3.72      ,  3.72093023,  3.68493151,\
        3.72151899,  3.71084337,  3.70930233,  3.7027027 ,  3.71727749,\
        3.69230769,  3.67241379,  3.44117647,  3.29641694,  3.34375   ,\
        3.33423181,  3.22171946,  3.21991701,  3.09285714,  2.99543379,\
        2.95428571,  2.90921409,  2.89921466,  2.88076923,  2.87826087,\
        2.83568075,  2.7993311 ,  2.79325354,  2.77905759,  2.72173913,\
        2.69512195,  2.70872947,  2.71487603,  3.20012277,  3.49120235,\
        3.83892153,  3.86511628,  4.06751688,  4.14547437,  4.21015052,\
        4.21015052,  4.21015052,  4.21015052,  4.21015052,  4.21015052,\
        4.21015052,  4.21015052,  4.21015052,  4.21015052,  4.21015052,\
        4.21015052,  4.21015052,  4.21015052,  4.21015052,  4.21015052,\
        4.21015052,  4.21015052,  4.21015052,  4.21015052,  4.21015052,\
        4.21015052,  4.21015052,  4.21015052,  4.21015052,  4.21015052,\
        4.21015052,  4.21015052,  4.21015052,  4.21015052,  4.21015052,\
        4.21015052,  4.21015052,  4.21015052,  4.21015052,  4.21015052,\
        4.21015052,  4.21015052]
    data.append(data3)


    cf_params = [(0.2,1,8),(0.2,1,3),(0.2,1,8)]

    fig = plt.figure()
    for i in range(len(data)):
        ret = []
        param_r, param_order, param_smooth = cf_params[i]
        cf = changefinder.ChangeFinder(r = param_r, order = param_order, smooth = param_smooth)
        for j in range(len(data[i])):
            score = cf.update(data[i][j])
            ret.append(score)
        print [(ret[idx],data[i][idx]) for idx in range(len(ret))]
        ax = fig.add_subplot(3,1,i+1)
        ax.plot(range(len(data[i])),ret, 'b')
        ax2 = ax.twinx()
        ax2.plot(range(len(data[i])),data[i],'r')
    plt.show()

def checkCusum():
    x = numpy.random.randn(300)/5
    x[100:200] += numpy.arange(0, 4, 4/100)
    ta, tai, taf, amp = cm.detect_cusum(x, 2, .02, True, True)
    print ta, tai, taf, amp
    
def checkCusumCallRFromPy(x, shift = 1,stdev = None,decision_interval = 5, new_data = []):
    # x = numpy.random.randn(300)/5
    # x[100:200] += numpy.arange(0, 4, 4/100)
    import rpy2.robjects as robjects
    from rpy2.robjects.packages import importr
    qcc = importr("qcc")
    data = robjects.vectors.FloatVector(x)
    robjects.r('''
                cusum_rpy <- function(data, shift, new_data, std_dev=-1) {
                    if (std_dev == -1) {
                        out<-cusum(data, se.shift=shift, newdata=new_data, decision.interval=3, plot=FALSE)
                        return (out$violations)
                    }
                        out<-cusum(data, se.shift=shift, std.dev=std_dev, newdata=new_data, decision.interval=3, plot=FALSE)
                        return (out$violations)
                }
                ''')
    cusum_rpy = robjects.globalenv['cusum_rpy']
    if stdev != None:
        out = cusum_rpy(data, shift, new_data, std_dev = stdev)
    else:
        out = cusum_rpy(data, shift, new_data)
    output = dict(out.items())
    output = {k:[val-1 for val in list(v)] for k,v in output.items()}
    return output['upper'],output['lower']
    
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
    ax.axvline(x=5, ymin=data[5]/max(data), linewidth=2, color='r')
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
    
    bnssKeySet = set(bnssKeys[:1])

    bnss_statistics = measure_extractor.extractMeasures(usrIdToUserDict,bnssIdToBusinessDict,reviewIdToReviewsDict,\
                     superGraph, cross_time_graphs, plotDir, bnssKeySet, timeLength)
    
    chPtsOutliers = AnomalyDetector.detectChPtsAndOutliers(bnss_statistics)
    
    total_time_slots = len(cross_time_graphs.keys())
    
    PlotUtil.plotter(bnssKeySet, bnss_statistics, chPtsOutliers,\
                      bnssIdToBusinessDict, total_time_slots, plotDir)


def cusum_using_call_to_r_py(x):
    changes = []
    idx = 0
    std_dev = None
    for i in range(1, x.size):
        # print '-------------------------------'
        # print i
        #print x[idx:i], x[i]
        if std_dev == None:
            upper_l, lower_l = checkCusumCallRFromPy(x[idx:i], shift=0.5, new_data=x[i])
        # else:
        #     upper_l, lower_l = checkCusumCallRFromPy(x[idx:i], shift=0.5, stdev=std_dev, new_data=x[i])
        std_dev = None
        # print 'sample<-c(',
        # for j in range(idx,i):
        # print x[j],
        #     if j != i:
        #         print ',',
        # print ')'
        # print 'new_d<-c(',x[i],')'
        #print [idx + val for val in upper_l], [idx + val for val in lower_l]
        # print '-------------------------------'
        if i - idx in upper_l or i - idx in lower_l:
            # if std_dev == None:
            #     std_dev = numpy.std(x[idx:i])
            idx = i
            changes.append(idx)
    return changes


def plotCusumChanges(x, changes, detection_times=[]):

    fig = plt.figure()
    ax1 = fig.add_subplot(1, 1, 1)
    ax1.plot(x)
    plt.ylim((1,5))
    plt.yticks(numpy.arange(1,5.5,0.5))
    ax1.plot(changes, x[changes], 'o', mfc='r', mec='r', mew=1, ms=5,
             label='Alarm')
    if len(detection_times) > 0:
        ax1.plot(detection_times, x[detection_times], 'o', mfc='g', mec='g', mew=1, ms=5,
                 label='Detection')
    plt.show()


def testCusum():
    data = numpy.concatenate([numpy.random.normal(0.7, 0.05, 200), numpy.random.normal(1.5, 0.05, 200),\
                              numpy.random.normal(2.3, 0.05, 200)])
    data = numpy.concatenate([numpy.random.normal(0.7, 0.05, 200), numpy.random.normal(0.7, 0.4, 200)])
    data = numpy.concatenate([numpy.random.normal(0.7, 0.05, 200), numpy.random.normal(0.7, 0.2, 200)])
    data = [0.71912204,0.87731491,1.04376258,1.40563906,0.88967452,0.54856211
            ,0.53175152,0.55124426,0.55343821,0.62240886,0.74833934,0.85191151
            ,0.7632238,0.79266917,0.94361834,1.04220472,1.02522303,0.52746524
            ,0.19799156,0.6144071,0.58449179,0.63295556,0.93026894,0.7709049
            ,0.53611494,0.74182611,0.96449673,0.8470438,0.98779719,0.81249067
            ,0.84709773,0.87185117,0.82816918,0.27686884,0.04748681,0.12145272
            ,0.1041873,0.31396252,0.07103816,0.15854998,0.10125327,0.09326488
            ,0.07942194,0.03908175,0.11218925,0.10670825,0.2035722,0.2035722
            ,0.2035722,0.2035722,0.2035722,0.2035722,0.2035722,0.2035722
            ,0.2035722,0.2035722,0.2035722,0.2035722,0.2035722,0.2035722
            ,0.2035722,0.2035722,0.2035722,0.2035722,0.2035722,0.2035722
            ,0.2035722,0.2035722,0.2035722,0.2035722,0.2035722,0.2035722
            ,0.2035722,0.2035722,0.2035722,0.2035722,0.2035722,0.2035722
            ,0.2035722,0.2035722,0.2035722,0.0,0.0]
    data = [3.32919255,3.64074074,3.84269663,3.90813648,4.00207039,4.12747875
,4.17529039,4.2212766,4.24964639,4.22222222,4.22419725,4.2175552
,4.23211606,4.24624765,4.25167936,4.25248166,4.2575,4.25680787
,4.29813318,4.30547474,4.29731762,4.29461078,4.28444652,4.26276548
,4.24914237,4.23062539,4.20832483,4.15762171,4.13535749,4.0970021
,4.06199813,4.03958944,4.0111131,4.07295029,4.46319569,4.50791645
,4.5365574,4.53393311,4.58877685,4.59767227,4.57510136,4.58629547
,4.59982221,4.60221015,4.61307239,4.62219092,4.62106638,4.62106638
,4.62106638,4.62106638,4.62106638,4.62106638,4.62106638,4.62106638
,4.62106638,4.62106638,4.62106638,4.62106638,4.62106638,4.62106638
,4.62106638,4.62106638,4.62106638,4.62106638,4.62106638,4.62106638
,4.62106638,4.62106638,4.62106638,4.62106638,4.62106638,4.62106638
,4.62106638,4.62106638,4.62106638,4.62106638,4.62106638,4.62106638
,4.62106638,4.62106638,4.62106638,4.62105966,4.62105966]

    x = numpy.atleast_1d(data).astype('float64')
    changes = cusum_using_call_to_r_py(x)
    plotCusumChanges(changes, x)

    #ta, tai, tapi, tani = AnomalyDetector.detect_outliers_using_cusum(data, 0.5)
    #print ta
    plotCusumChanges(ta, x)

def tryAr():
    fig = plt.figure()
    ax1 = fig.add_subplot(1, 1, 1)
    import statsmodels.api as sm
    data = numpy.random.normal(0.7,0.05,100)
    ax1.plot(data, 'b')
    ar = sm.tsa.AR(data)
    ar_mod = ar.fit()
    print ar_mod.params

    # import statsmodels.tsa.arima_model as ari
    #
    # model=ari.ARMA(data[:20],(1,1))
    # ar_res= model.fit()
    # preds=ar_res.predict(21,100)
    # print preds

def runChangeFinder(data, show=True):
    ret = []
    cf = changefinder.ChangeFinder(r=0.2, order=1, smooth=4)
    fig = plt.figure()
    for i in range(len(data)):
        score = cf.update(data[i])
        ret.append(score)
    print ret
    if show:
        # idxs = argrelextrema(numpy.array(ret), numpy.greater)
        #print idxs,type(idxs)
        ax1 = fig.add_subplot(1, 1, 1)
        ax1.plot(data, 'r')
        #plt.ylim((0,3))
        ax2 = ax1.twinx()
        ax2.plot(ret, 'b')
        # for idx in idxs:
        #     ax2.axvline(x=idx, ymin=ret[idx]/max(ret), linewidth=2, color='g')
        plt.show()




def testChangeFinder():
    data = numpy.concatenate([numpy.random.normal(5,3,10),numpy.random.normal(10,3,10)])
    # for i in range(1,len(data)):
    #     data[i] += data[i-1]
    #data = numpy.concatenate([numpy.array([0.8,0.9,0.7,1,0.4,0.9,0.6,1.1]),numpy.random.normal(0.7,0.05,10)])
    data = [ 51,2059,5640,7973,11302,13875,18269,23166,27936,35568,39055,41634
            ,42239,42239,42239,42239,42239,42239,42239,42239,42239,42239,42239,42239
            ,42239,42239,42239,42239,42239,42239,42239,42239,42239,42239,42239,42239
            ,42239,42239,42239,42239,42239,42239,42239,42239,42241,42242,42245,42247
            ,42247]
    runChangeFinder(data)

def testCumsumWithData():
    data =[4.4, 3.73469388,3.79032258,3.76470588,3.73239437,3.72972973
            ,3.74766355,3.69298246,3.76033058,3.72093023,3.67375887,3.7133758
            ,3.70807453,3.7,3.69945355,3.71276596,3.71144279,3.67431193
            ,3.55294118,3.32312925,3.34302326,3.35654596,3.28678304,3.22173913
            ,3.15799615,3.04133545,2.95827338,2.92797784,2.8972332, 2.89262613
            ,2.87641866,2.83928571,2.81044268,2.79299014,2.78181818,2.74556213
            ,2.7037037, 2.72035398,2.70134228,2.7196414, 3.47996042,3.73190661
            ,3.8638796, 4.04405631,4.06884596,4.21015052,4.21015052,4.21015052
            ,4.21015052,4.21015052,4.21015052,4.21015052,4.21015052,4.21015052
            ,4.21015052,4.21015052,4.21015052,4.21015052,4.21015052,4.21015052
            ,4.21015052,4.21015052,4.21015052,4.21015052,4.21015052,4.21015052
            ,4.21015052,4.21015052,4.21015052,4.21015052,4.21015052,4.21015052
            ,4.21015052,4.21015052,4.21015052,4.21015052,4.21015052,4.21015052
            ,4.21015052,4.21015052,4.21015052,4.21015052,4.21015052,4.21015052]

    ta, tai, taf, amp = cm.detect_cusum(data,threshold=0.5,show=True)
    #runChangeFinder(data,show=True)
    print ta, tai, taf, amp
    fig = plt.figure(figsize=(20,20))
    ax1 = fig.add_subplot(1, 1, 1)
    ax1.plot(range(0,len(data)),data)
    plt.ylim((1,5))
    plt.yticks(numpy.arange(1,5.5,0.5))
    for i in range(len(ta)):
        alarm_time_idx = ta[i]
        alarm_start_idx = tai[i]
        ax1.axvline(x=alarm_time_idx,linewidth=2, color='r')
    plt.show()




def testAVGplot():
    data1=[3.32919255,3.64074074,3.84269663,3.90813648,4.00207039,4.12747875
,4.17529039,4.2212766,4.24964639,4.22222222,4.22419725,4.2175552
,4.23211606,4.24624765,4.25167936,4.25248166,4.2575,4.25680787
,4.29813318,4.30547474,4.29731762,4.29461078,4.28444652,4.26276548
,4.24914237,4.23062539,4.20832483,4.15762171,4.13535749,4.0970021
,4.06199813,4.03958944,4.0111131,4.07295029,4.46319569,4.50791645
,4.5365574,4.53393311,4.58877685,4.59767227,4.57510136,4.58629547
,4.59982221,4.60221015,4.61307239,4.62219092,4.62106638,4.62106638
,4.62106638,4.62106638,4.62106638,4.62106638,4.62106638,4.62106638
,4.62106638,4.62106638,4.62106638,4.62106638,4.62106638,4.62106638
,4.62106638,4.62106638,4.62106638,4.62106638,4.62106638,4.62106638
,4.62106638,4.62106638,4.62106638,4.62106638,4.62106638,4.62106638
,4.62106638,4.62106638,4.62106638,4.62106638,4.62106638,4.62106638
,4.62106638,4.62106638,4.62106638,4.62105966,4.62105966]


    data2 = [3.36,3.28712871,3.3483871,3.4173913,3.59032258,3.58791209
,3.60294118,3.62700229,3.61684211,3.61320755,3.63427562,3.64548495
,3.64808917,3.6578125,3.65846154,3.64497041,3.62716763,3.63496503
,3.61580381,3.61170213,3.57474227,3.57088608,3.5408039,3.51306413
,3.49655172,3.44555556,3.41550054,4.19930676,4.59377971,4.62541237
,4.64245544,4.65523777,4.68450056,4.68450056,4.68450056,4.69760116
,4.70102499,4.71395594,4.71809626,4.71809626,4.71809626,4.71809626
,4.71809626,4.71809626,4.71809626,4.71809626,4.71809626,4.71809626
,4.71809626,4.71809626,4.71809626,4.71809626,4.71809626,4.71809626
,4.71809626,4.71809626,4.71809626,4.71809626,4.71809626,4.71809626
,4.71809626,4.71809626,4.71809626,4.71809626,4.71809626,4.71809626
,4.71809626,4.71809626,4.71809626,4.71809626,4.71809626,4.71809626
,4.71809626,4.71809626,4.71809626]


    data3 = [3.83221477,3.55299539,3.25,3.18020305,3.64212077,3.65085837
,3.59494333,3.50950629,3.48125808,3.43387739,3.39578898,3.22815285
,3.17549029,3.14201898,3.08793062,3.03221516,3.01286648,3.00580919
,3.00536102,3.00515498,2.96031996,2.94514013,2.93650337,2.92073815
,2.89103543,2.88920306,2.88920306,2.88920306,2.88920306,2.88920306
,2.88920306,2.88920306,2.88920306,2.88920306,2.88920306,2.88920306
,2.88920306,2.88920306,2.88920306,2.88920306,2.88920306,2.88920306
,2.88920306,2.88920306,2.88920306,2.88920306,2.88920306,2.88920306
,2.88920306,2.88920306,2.88920306,2.88920306,2.88920306,2.88920306
,2.88920306,2.88920306,2.88920306,2.88905178,2.88905178,2.88905178
,2.8891623,2.8891623]


    data4 = [2.66666667,4.30120482,4.31009957,4.33190091,4.33910035,4.33901866
,4.35712855,4.36539133,4.37286401,4.37955437,4.37966194,4.37904216
,4.37781558,4.37735977,4.37623695,4.37168679,4.36491841,4.34945627
,4.34415109,4.34063163,4.33732945,4.3366638,4.2955183,4.29255423
,4.28257202,4.28099495,4.27846383,4.27801822,4.27700045,4.27543792
,4.27494371,4.27506592,4.27506592,4.27506592,4.27506592,4.27506592
,4.27506592,4.27506592,4.27506592,4.27506592,4.27506592,4.27506592
,4.27506592,4.27506592,4.27506592,4.27506592,4.27506592,4.27506592
,4.27506592,4.27506592,4.27506592,4.27506592,4.27506592,4.27506592
,4.27506592,4.27506592,4.27506592,4.27506592,4.27506592,4.27506592
,4.27506592,4.27506592,4.27506592,4.27506592,4.27506592,4.27506592
,4.27506592,4.27506592]

    data5 = [4.68181818,4.64930556,4.67321429,4.69469599,4.68819599,4.68023833
,4.66281139,4.65711879,4.64947623,4.62684251,4.6029318,4.52859779
,4.50938776,4.50338681,4.48964837,4.49208812,4.49186047,4.49156902
,4.49156902,4.49156902,4.49156902,4.49156902,4.49156902,4.49156902
,4.49156902,4.49156902,4.49536387,4.50124688,4.50124688,4.50124688
,4.50124688,4.50124688,4.50124688,4.50124688,4.50124688,4.50124688
,4.50124688,4.50124688,4.50124688,4.50124688,4.50124688,4.50124688
,4.50124688,4.50124688,4.50124688,4.50124688,4.50124688,4.50124688
,4.50124688,4.50124688,4.50124688,4.50124688,4.50124688,4.50124688
,4.50124688,4.50124688,4.50124688,4.50124688,4.50124688,4.50124688
,4.50124688,4.50124688,4.50124688,4.50124688]

    data = [data1,data2,data3,data4,data5]
    #data = [numpy.concatenate([numpy.random.normal(3.5,0.1,100),numpy.random.normal(4.1,0.2,100)])]
    for d in data:
        d = numpy.atleast_1d(d).astype('float64')
        ta, tai, tapi, tani = AnomalyDetector.detect_outliers_using_cusum(d,threshold=0.5)
        # up,low = checkCusumCallRFromPy(d,0.5,new_data=[])
        # changes = sorted(up+low)
        plotCusumChanges(ta, d)

def checkCusum2():
    changes = []
    detection_times = []
    idx = 0
    data = [3.83221477,3.55299539,3.25,3.18020305,3.64212077,3.65085837
,3.59494333,3.50950629,3.48125808,3.43387739,3.39578898,3.22815285
,3.17549029,3.14201898,3.08793062,3.03221516,3.01286648,3.00580919
,3.00536102,3.00515498,2.96031996,2.94514013,2.93650337,2.92073815
,2.89103543,2.88920306,2.88920306,2.88920306,2.88920306,2.88920306
,2.88920306,2.88920306,2.88920306,2.88920306,2.88920306,2.88920306
,2.88920306,2.88920306,2.88920306,2.88920306,2.88920306,2.88920306
,2.88920306,2.88920306,2.88920306,2.88920306,2.88920306,2.88920306
,2.88920306,2.88920306,2.88920306,2.88920306,2.88920306,2.88920306
,2.88920306,2.88920306,2.88920306,2.88905178,2.88905178,2.88905178
,2.8891623,2.8891623]
    x = numpy.atleast_1d(data).astype('float64')
    i = 1
    print x.size
    for i in range(1, x.size):
        upper_l, lower_l = checkCusumCallRFromPy(x[idx:i], shift=1, new_data=x[i])
        if len(upper_l) > 0 or len(lower_l)>0:
            ch = sorted([idx+j for j in upper_l]+[idx+j for j in lower_l])
            print idx,i,x[idx:i],x[i]
            changes = changes+ch
            detection_times.append(i)
            idx = i
        #i+=1
    changes = sorted(list(set(changes)))
    print changes
    print detection_times
    plotCusumChanges(x, changes, detection_times)

#testCusum()
#testCFForSomeMeasures()
#tryTemporalStatisticsForItunes()
#checkPlot2()
#setMemUsage()
#testCumsumWithData()
#checkDataFrame()
#tryAr()
#testAVGplot()
checkCusum2()