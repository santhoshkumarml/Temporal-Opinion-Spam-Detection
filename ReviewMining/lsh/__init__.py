# -*- coding: utf-8 -*-
from util.ScrappedDataReader import ScrappedDataReader as sdr
from util.GraphUtil import TemporalGraph
from util import SIAUtil
import ShingleUtil
import sys
import numpy


def checkJacDocHash(inputDirName):
    scr = sdr()
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