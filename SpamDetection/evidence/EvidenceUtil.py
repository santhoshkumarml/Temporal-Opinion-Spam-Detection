'''
@author: santhosh
'''
import collections
import datetime
import nltk
import numpy
import os, math, pandas as pd

import matplotlib.pyplot as plt
import networkx as nx
import phrase_wise_rev_pn
from util import GraphUtil, SIAUtil, PlotUtil
from util.data_reader_utils.swm_utils.SWMDataReader import SWMDataReader
from util.text_utils import LDAUtil, TextConstants
from main import AppUtil
import matplotlib

import pickle
import sys


nltk.data.path.append(TextConstants.NLTK_DATA_PATH)

TIME_WISE_RATING = 'Time Wise Rating Count'
RATING_DISTRIBUTION = 'Rating Distribution'
EXTREMITY_OF_NON_SINGLETON_USERS = 'Extremity of Non Singleton Users'
SUSPICIOUSNESS_GRAPH = 'Suspicious Non Singleton User'

def make_autopct(values):
    def my_autopct(pct):
        total = sum(values)
        val = int(round(pct*total/100.0))
        if val == 0:
            return ''
        return '{v:d}'.format(p=pct, v=val)
    return my_autopct

def sortAndPrintReviewsInfo(plotDir, superGraph):
    bnss_ids = []
    usr_ids = []
    dates = []
    txts = []
    for reviewId in superGraph.getReviewIds():
        r = superGraph.getReviewFromReviewId(reviewId)
        txt = str(r.getReviewText())
        if not txt or txt == '':
            continue
        bnss_id = str(r.getBusinessID())
        usr_id = str(r.getUserId())
        d = SIAUtil.getDateForReview(r).strftime('%m/%d/%y')
        bnss_ids.append(bnss_id)
        usr_ids.append(usr_id)
        dates.append(d)
        txts.append(txt)
    d = {'bnss': bnss_ids, 'usr': usr_ids, 'dates': dates, 'text': txts}
    df = pd.DataFrame(d)
    df.info()
    with open(os.path.join(plotDir, 'sorted_reviews.csv'), 'w') as f:
        print 'Started The File Write'
        df.to_csv(f, escapechar='\\', columns=['bnss', 'usr', 'dates', 'text'])
        print 'Finished The File Write'

def plotSusGraph(non_singleton_usr_suspicousness,
                 non_singleton_usr_non_suspicousness,
                            imgFolder, time_key_to_date_time,
                            title='Suspicious Non Singleton User',
                            plot_non_suspicious=False):
    fig = plt.figure(figsize=(24, 16))
    imgFile = os.path.join(imgFolder, title + '.png')

    g = nx.Graph()
    bnss_nodes = set()
    usr_nodes = set()

    node_labels = dict()

    for usrId in non_singleton_usr_suspicousness.keys():
        for revw_for_usr in non_singleton_usr_suspicousness[usrId]:
            bnss_id_for_revw = revw_for_usr.getBusinessID()
            date_time_for_this_usr = SIAUtil.getDateForReview(revw_for_usr)

            time_id_for_date_time = findTimeIdForDateTime(time_key_to_date_time,\
                                                          date_time_for_this_usr)
            bnss_nodes.add(bnss_id_for_revw)
            g.add_edge(usrId, bnss_id_for_revw, {'edge': (revw_for_usr.getRating(), time_id_for_date_time)})

            node_labels[bnss_id_for_revw] = bnss_id_for_revw
            usr_nodes.add(usrId)
            node_labels[usrId] = usrId

    edge_labels=dict([((u,v,),d['edge']) for u,v,d in g.edges(data=True)])

    usr_nodes_len = len(usr_nodes)
    bnss_nodes_len = len(bnss_nodes)

    pos = dict()

    usr_node_iter = bnss_nodes_len
    for node in usr_nodes:
        pos[node] = (1, usr_node_iter)
        usr_node_iter += bnss_nodes_len

    bnss_nodes_iter = usr_nodes_len
    for node in bnss_nodes:
        pos[node] = (4, bnss_nodes_iter)
        bnss_nodes_iter += usr_nodes_len

    nx.draw_networkx_nodes(g, pos,
                           nodelist=list(usr_nodes),
                           node_color='b',
                           node_size=500,
                           alpha=0.8)
    nx.draw_networkx_nodes(g, pos,
                           nodelist=list(bnss_nodes),
                           node_color='m',
                           node_size=500,
                           alpha=0.8)

    nx.draw_networkx_edges(g, pos,
                       edgelist=[(usrId, revw_for_usr.getBusinessID())
                                 for usrId in non_singleton_usr_suspicousness.keys()
                                 for revw_for_usr in non_singleton_usr_suspicousness[usrId]],
                       alpha=0.5, edge_color='r', width=1.0)


    # nx.draw_networkx_edges(g, pos, width=1.0, alpha=0.5)
    nx.draw_networkx_edge_labels(g, pos, edge_labels=edge_labels,\
                                 label_pos= 0.3)

    plt.title(title)
    plt.axis('off')
    PlotUtil.savePlot(imgFile)

def plotSuspiciousNessGraph(non_singleton_usr_suspicousness,
                            non_singleton_usr_non_suspicousness,
                            imgFolder, time_key_to_date_time,
                            title='Suspicious Non Singleton User',
                            plot_non_suspicious=False):
    fig = plt.figure(figsize=(24, 16))
    imgFile = os.path.join(imgFolder, title + '.png')

    g = nx.Graph()
    bnss_nodes = set()
    usr_nodes = set()

    node_labels = dict()

    for usrId in non_singleton_usr_suspicousness.keys():
        for revw_for_usr in non_singleton_usr_suspicousness[usrId]:
            bnss_id_for_revw = revw_for_usr.getBusinessID()
            date_time_for_this_usr = SIAUtil.getDateForReview(revw_for_usr)

            time_id_for_date_time = findTimeIdForDateTime(time_key_to_date_time,\
                                                          date_time_for_this_usr)
            bnss_nodes.add(bnss_id_for_revw)
            g.add_edge(usrId, bnss_id_for_revw, {'edge': (revw_for_usr.getRating(), time_id_for_date_time)})

            node_labels[bnss_id_for_revw] = bnss_id_for_revw
            usr_nodes.add(usrId)
            node_labels[usrId] = usrId

    if plot_non_suspicious:
        for usrId in non_singleton_usr_non_suspicousness.keys():
            for revw_for_usr in non_singleton_usr_non_suspicousness[usrId]:
                bnss_id_for_revw = revw_for_usr.getBusinessID()
                date_time_for_this_usr = SIAUtil.getDateForReview(revw_for_usr)

                time_id_for_date_time = findTimeIdForDateTime(time_key_to_date_time,\
                                                              date_time_for_this_usr)
                bnss_nodes.add(bnss_id_for_revw)
                g.add_edge(usrId, bnss_id_for_revw, {'edge': (revw_for_usr.getRating(),
                                                               time_id_for_date_time)})
                node_labels[bnss_id_for_revw] = bnss_id_for_revw
                usr_nodes.add(usrId)
                node_labels[usrId] = usrId

    edge_labels=dict([((u,v,),d['edge']) for u,v,d in g.edges(data=True)])

    usr_nodes_len = len(usr_nodes)
    bnss_nodes_len = len(bnss_nodes)

    pos = dict()

    usr_node_iter = bnss_nodes_len
    for node in usr_nodes:
        pos[node] = (1, usr_node_iter)
        usr_node_iter += bnss_nodes_len

    bnss_nodes_iter = usr_nodes_len
    for node in bnss_nodes:
        pos[node] = (4, bnss_nodes_iter)
        bnss_nodes_iter += usr_nodes_len

    nx.draw_networkx_nodes(g, pos,
                           nodelist=list(usr_nodes),
                           node_color='b',
                           node_size=500,
                           alpha=0.8)
    nx.draw_networkx_nodes(g, pos,
                           nodelist=list(bnss_nodes),
                           node_color='m',
                           node_size=500,
                           alpha=0.8)

    nx.draw_networkx_edges(g, pos,
                       edgelist=[(usrId, revw_for_usr.getBusinessID())
                                 for usrId in non_singleton_usr_suspicousness.keys()
                                 for revw_for_usr in non_singleton_usr_suspicousness[usrId]],
                       alpha=0.5, edge_color='r')

    if plot_non_suspicious:
        nx.draw_networkx_edges(g, pos,
                               edgelist=[(usrId, revw_for_usr.getBusinessID())
                                         for usrId in non_singleton_usr_non_suspicousness.keys()
                                         for revw_for_usr in non_singleton_usr_non_suspicousness[usrId]],
                               alpha=0.5, edge_color='g')

    nx.draw_networkx_labels(g, pos, labels=node_labels)
    # nx.draw_networkx_edges(g, pos, width=1.0, alpha=0.5)
    for edge_label in edge_labels:
        nx.draw_networkx_edge_labels(g, pos, edge_labels=edge_labels,\
                                     label_pos= 0.3)

    plt.title(title)
    plt.axis('off')
    PlotUtil.savePlot(imgFile)


def plotRatingDistribution(review_rating_distribution, imgFolder,
                           title='Rating Distribution'):
    fig = plt.figure(figsize=(20, 20))

    colors = {1.0:'y', 2.0:'c', 3.0:'m', 4.0:'g', 5.0:'r'}

    ax = plt.axes([0.1, 0.1, 0.8, 0.8])
    imgFile = os.path.join(imgFolder, title)

    refined_review_rating_distribution = {key: review_rating_distribution[key] for key in review_rating_distribution}

    labels = refined_review_rating_distribution.keys()
    colors = [colors[label] for label in labels]
    labels = [int(label) for label in labels]
    fracs = refined_review_rating_distribution.values()

    patches, texts, autotexts = ax.pie(fracs, labels=labels, autopct=make_autopct(fracs), shadow=False, startangle=90, colors=colors, labeldistance=1.15, pctdistance= 0.8)

    for text in texts:
        text.set_fontsize(36)

    for text in autotexts:
        text.set_fontsize(50)

    plt.title(title, fontsize=40)

    plt.legend(prop={'size':36})

    PlotUtil.savePlot(imgFile)


def plotExtremityForNonSingletonUsr(extreme_usrs, non_extreme_usrs, imgFolder,
                                    title='Extremity of Non Singleton Users'):
    fig = plt.figure(figsize=(18, 8))
    ax = fig.add_subplot(1, 1, 1)
    width = 0.20
    imgFile = os.path.join(imgFolder, title + '.png')
    x_labels = ['Extreme Users', 'Non Extreme Users']
    p_extreme = ax.bar(0, extreme_usrs, width, color='r')
    p_non_extreme = ax.bar(0.5, non_extreme_usrs, width, color='b')

    plt.ylabel('Count')
    plt.title(title)
    plt.xticks([0.10, 0.60], x_labels)
    plt.legend(prop={'size':50})
    PlotUtil.savePlot(imgFile)

def plotReviewTimeRating(review_time_rating, imgFolder, title='Time Wise Rating Count'):
    fig = plt.figure(figsize=(32, 16))
    ax = fig.add_subplot(1, 1, 1)
    imgFile = os.path.join(imgFolder, title)
    colors = {1.0:'y', 2.0:'c', 3.0:'m', 4.0:'g', 5.0:'r'}
    total_days = len(review_time_rating[1.0].keys())
    indxs = numpy.arange(0, total_days * 4, 4)
    week_indxs = [idx for idx in indxs if ((idx % 7) == 0)]
    width = 3.8
    x_labels = [d.strftime('%m/%d') for d in sorted(review_time_rating[1.0].keys())]
    pS = []
    btm = None
    for rating_key in sorted(review_time_rating.keys()):
        val = review_time_rating[rating_key]
        od = collections.OrderedDict(sorted(val.items()))
        val = numpy.array(od.values())
        if btm is None:
            p = ax.bar(indxs, val, width, color=colors[rating_key])
            btm = val
        else:
            p = ax.bar(indxs, val, width, color=colors[rating_key], bottom=btm)
            btm = numpy.array([btm[i] + val[i] for i in range(0, total_days)])

        pS.append(p)

    for idx in week_indxs:
        ax.axvline(x=idx, ymin=0, ymax=1000000, linewidth=3, color='black')

    plt.ylabel(title)
#     plt.title(title)
    plt.xticks(indxs + width/2., x_labels)
    plt.legend([p[0] for p in pS], range(1, 6), prop={'size':50}, loc='best')
#     fontsize = 30, handlelength=6, borderpad=1, labelspacing=2

#     params = {'legend.fontsize': 20}
#     plt.rcParams.update(params)

    for item in (ax.get_xticklabels()):
        item.set_fontsize(31)

    for item in (ax.get_yticklabels()):
        item.set_fontsize(60)

    ax.yaxis.label.set_fontsize(45)

    plt.tight_layout()

    PlotUtil.savePlot(imgFile, isPdf=True)



def getNecessaryDs(csvFolder, rdr=SWMDataReader(), readReviewsText=False, timeLength='1-W'):
    suspicious_timestamps = dict()
    suspicious_timestamp_ordered = list()
    with open(os.path.join(csvFolder, 'out_all_features_mul_reviews.log')) as f:
        lines = f.readlines()
        for line in lines:
            bnss_key, idx1, idx2, score = line.strip().split()
            idx1 = int(idx1[1:-1])
            idx2 = int(idx2[:-1])
            if bnss_key not in suspicious_timestamps:
                suspicious_timestamps[bnss_key] = set()
            for idx in range(idx1, idx2):
                suspicious_timestamps[bnss_key].add(idx)
            suspicious_timestamp_ordered.append((bnss_key, (idx1, idx2)))
    bnssIdToBusinessDict, reviewIdToReviewsDict, usrIdToUserDict = AppUtil.readData(csvFolder,
                                                                            readReviewsText=readReviewsText, rdr=rdr)
    ctg = GraphUtil.createTemporalGraph(usrIdToUserDict,
                                        bnssIdToBusinessDict,
                                        reviewIdToReviewsDict,
                                        timeLength)
    superGraph = GraphUtil.createSuperGraph(usrIdToUserDict, bnssIdToBusinessDict,
                                            reviewIdToReviewsDict, timeLength)
    time_key_to_date_time = dict()
    for t_k in ctg.keys():
        d = ctg[t_k].getDateTime()
        time_key_to_date_time[t_k] = d

    # del time_key_to_date_time, suspicious_timestamps, superGraph, ctg

    return ctg, superGraph, time_key_to_date_time, suspicious_timestamps, suspicious_timestamp_ordered

def plotGraphForReviewText(review_ids, superGraph, imgFolder, title, text, time_key_to_date_time):
    fig = plt.figure(figsize=(24, 16))
    imgFile = os.path.join(imgFolder, title + '.png')

    g = nx.Graph()
    bnss_nodes = set()
    singleton_usr_nodes = set()
    non_singleton_usr_nodes = set()

    node_labels = dict()

    for revwId in review_ids:
        revw = superGraph.getReviewFromReviewId(revwId)
        bnss_id_for_revw = revw.getBusinessID()
        usrId = revw.getUserId()
        date_time_for_this_usr = SIAUtil.getDateForReview(revw)

        time_id_for_date_time = findTimeIdForDateTime(time_key_to_date_time,\
                                                      date_time_for_this_usr)
        bnss_nodes.add(bnss_id_for_revw)
        g.add_edge(usrId, bnss_id_for_revw, {'edge': (revw.getRating(), time_id_for_date_time)})

        node_labels[bnss_id_for_revw] = bnss_id_for_revw
        if len(superGraph.neighbors((usrId, SIAUtil.USER))) == 1:
            singleton_usr_nodes.add(usrId)
        else:
            non_singleton_usr_nodes.add(usrId)
        node_labels[usrId] = usrId

    edge_labels=dict([((u,v,),d['edge']) for u,v,d in g.edges(data=True)])

    usr_nodes_len = len(singleton_usr_nodes) + len(non_singleton_usr_nodes)
    bnss_nodes_len = len(bnss_nodes)

    pos = dict()

    usr_node_iter = bnss_nodes_len

    for node in singleton_usr_nodes:
        pos[node] = (1, usr_node_iter)
        usr_node_iter += bnss_nodes_len

    for node in non_singleton_usr_nodes:
        pos[node] = (1, usr_node_iter)
        usr_node_iter += bnss_nodes_len

    bnss_nodes_iter = usr_nodes_len
    for node in bnss_nodes:
        pos[node] = (4, bnss_nodes_iter)
        bnss_nodes_iter += usr_nodes_len

    nx.draw_networkx_nodes(g, pos,
                           nodelist=list(singleton_usr_nodes),
                           node_color='b',
                           node_size=500,
                           alpha=0.8)

    nx.draw_networkx_nodes(g, pos,
                           nodelist=list(non_singleton_usr_nodes),
                           node_color='g',
                           node_size=500,
                           alpha=0.8)

    nx.draw_networkx_nodes(g, pos,
                           nodelist=list(bnss_nodes),
                           node_color='m',
                           node_size=500,
                           alpha=0.8)

    nx.draw_networkx_edges(g, pos,
                       edgelist=[(superGraph.getReviewFromReviewId(revwId).getUserId(),
                                  superGraph.getReviewFromReviewId(revwId).getBusinessID())
                                 for revwId in review_ids],
                       alpha=0.5, edge_color='r')

    nx.draw_networkx_labels(g, pos, labels=node_labels)
    nx.draw_networkx_edge_labels(g, pos, edge_labels=edge_labels,\
                                 label_pos= 0.3)

    plt.title(title)
    ax = plt.gca()

    ax.text(0.95, 0.01, text,
        verticalalignment='bottom', horizontalalignment='right',
        transform=ax.transAxes,
        color='black', fontsize=15)

    plt.axis('off')
    PlotUtil.savePlot(imgFile)



def plotAllStats(time_wise_non_singleton_usr_suspicousness,\
                  time_wise_non_singleton_usr_non_suspicousness,\
                  time_wise_four_grams_dict,\
                  time_wise_three_grams_dict, time_wise_two_grams_dict,\
                  time_wise_all_user_review_rating_distribution,\
                  time_wise_singleton_review_rating_distribution,\
                  time_wise_non_singleton_review_rating_distribution,\
                  time_wise_extreme_non_singleton_usrs,\
                  time_wise_non_extreme_non_singleton_usrs,\
                  time_wise_review_time_rating,\
                  time_key_start, time_key_end, time_key_to_date_time,\
                  bnssImgFolder, statsToPlot = []):
    for time_key in range(time_key_start, time_key_end):
        imgFolder = os.path.join(bnssImgFolder, str(time_key))
        if RATING_DISTRIBUTION in statsToPlot or SUSPICIOUSNESS_GRAPH in statsToPlot:
            if not os.path.exists(imgFolder):
                os.makedirs(imgFolder)
        all_user_review_rating_distribution = time_wise_all_user_review_rating_distribution[time_key]
        singleton_review_rating_distribution = time_wise_singleton_review_rating_distribution[time_key]
        non_singleton_review_rating_distribution = time_wise_non_singleton_review_rating_distribution[time_key]
        extreme_non_singleton_usrs, non_extreme_non_singleton_usrs = time_wise_extreme_non_singleton_usrs[time_key], time_wise_non_extreme_non_singleton_usrs[time_key]
        non_singleton_usr_suspicousness, non_singleton_usr_non_suspicousness = time_wise_non_singleton_usr_suspicousness[time_key], time_wise_non_singleton_usr_non_suspicousness[time_key]
        if RATING_DISTRIBUTION in statsToPlot:
            plotRatingDistribution(all_user_review_rating_distribution, imgFolder,
                                   title='All Review Rating Count')
            plotRatingDistribution(singleton_review_rating_distribution, imgFolder,
                                   title='Singleton Review Rating Count')
            plotRatingDistribution(non_singleton_review_rating_distribution, imgFolder,
                                   title='Non Singleton Review Rating Count')
        if EXTREMITY_OF_NON_SINGLETON_USERS in statsToPlot:
            plotExtremityForNonSingletonUsr(extreme_non_singleton_usrs,
                                            non_extreme_non_singleton_usrs, imgFolder)
        if SUSPICIOUSNESS_GRAPH in statsToPlot:
            plotSusGraph(non_singleton_usr_suspicousness,
                          non_singleton_usr_non_suspicousness,
                          imgFolder, time_key_to_date_time,
                          plot_non_suspicious=False)

    if TIME_WISE_RATING in statsToPlot:
        if not os.path.exists(bnssImgFolder):
            os.makedirs(bnssImgFolder)
        plotReviewTimeRating(time_wise_review_time_rating,
                             bnssImgFolder)


def findTimeIdForDateTime(time_key_to_date_time, date_time_for_this_usr):
    time_id_for_date_time = -1
    for time_id in time_key_to_date_time.keys():
        if date_time_for_this_usr < time_key_to_date_time[time_id].date():
            break
        time_id_for_date_time = time_id
    return time_id_for_date_time


def printNGrams(time_key_start, time_key_end, time_wise_four_grams_dict,\
                time_wise_three_grams_dict, time_wise_two_grams_dict):
    for time_key in range(time_key_start, time_key_end):
        two_grams_dict = time_wise_two_grams_dict[time_key]
        three_grams_dict = time_wise_three_grams_dict[time_key]
        four_grams_dict = time_wise_four_grams_dict[time_key]
        print '------------------------', time_key, '----------------------------------------'
        print 'Two Grams'
        print sorted(two_grams_dict.iteritems(), key=lambda (gram, count):count, reverse=True)
        print 'Three Grams'
        print sorted(three_grams_dict.iteritems(), key=lambda (gram, count):count, reverse=True)
        print 'Four Grams'
        print sorted(four_grams_dict.iteritems(), key=lambda (gram, count):count, reverse=True)
        print '------------------------', time_key, '----------------------------------------'

def put_grams(grams, grams_dict):
    for gram in grams:
        if gram not in grams_dict:
            grams_dict[gram] = 0.0
        grams_dict[gram] += 1.0

def findStatsForEverything(plotDir,  bnssKey, time_key_wdw, necessaryDs, readReviewsText=False,
                            doPlot=False, statsToPlot = []):
    ctg, superGraph, time_key_to_date_time,\
     suspicious_timestamps, suspicious_timestamp_ordered = necessaryDs

    time_key_start, time_key_end = time_key_wdw

    time_wise_non_singleton_usr_suspicousness = {key: dict()\
                                                  for key in range(time_key_start, time_key_end)}
    time_wise_non_singleton_usr_non_suspicousness = {key: dict()\
                                                  for key in range(time_key_start, time_key_end)}
    time_wise_four_grams_dict = {key: dict()\
                                 for key in range(time_key_start, time_key_end)}
    time_wise_three_grams_dict = {key: dict()\
                                 for key in range(time_key_start, time_key_end)}
    time_wise_two_grams_dict = {key: dict()\
                                 for key in range(time_key_start, time_key_end)}

    time_wise_all_user_review_rating_distribution = {key:{float(key): 0.0 for key in range(1, 6)}\
                                                      for key in range(time_key_start, time_key_end)}
    time_wise_singleton_review_rating_distribution = {key:{float(key): 0.0 for key in range(1, 6)}\
                                                      for key in range(time_key_start, time_key_end)}
    time_wise_non_singleton_review_rating_distribution = {key:{float(key): 0.0 for key in range(1, 6)}\
                                                      for key in range(time_key_start, time_key_end)}

    time_wise_extreme_non_singleton_usrs = {key: 0\
                                 for key in range(time_key_start, time_key_end)}
    time_wise_non_extreme_non_singleton_usrs = {key: 0\
                                 for key in range(time_key_start, time_key_end)}

    time_wise_review_time_rating = {float(key): {(time_key_to_date_time[time_key]\
                                                 + datetime.timedelta(days=day_inc)).date(): 0.0\
                                                 for time_key in range(time_key_start, time_key_end)
                                                 for day_inc in range(0, 7)}
                                               for key in range(1, 6)}

    for time_key in range(time_key_start, time_key_end):
        G = ctg[time_key]
        if (bnssKey, SIAUtil.PRODUCT) not in G:
            continue
        neighboring_usr_nodes = G.neighbors((bnssKey, SIAUtil.PRODUCT))
        all_usrs = set([usrId for usrId, usr_type in neighboring_usr_nodes])
        singleton_usrs = set([usrId for usrId, usr_type in neighboring_usr_nodes
                      if len(superGraph.neighbors((usrId, usr_type))) == 1])
        non_singleton_usrs = all_usrs - singleton_usrs

        non_singleton_usr_suspicousness = time_wise_non_singleton_usr_suspicousness[time_key]
        non_singleton_usr_non_suspicousness = time_wise_non_singleton_usr_non_suspicousness[time_key]
        non_singleton_usr_all_review_distribution = dict()

        for non_singleton_usr in non_singleton_usrs:
            reviews_for_this_usr = sorted([superGraph.getReview(non_singleton_usr, bnssId) for (bnssId, bnss_type)
                                           in superGraph.neighbors((non_singleton_usr, SIAUtil.USER))])

            non_singleton_usr_all_review_distribution[non_singleton_usr] = {float(key): 0.0 for key in range(1, 6)}

            non_singleton_usr_suspicousness[non_singleton_usr] = list()

            non_singleton_usr_non_suspicousness[non_singleton_usr] = list()

            for revw_for_usr in reviews_for_this_usr:
                bnssId_for_this_review = revw_for_usr.getBusinessID()

                if bnssKey == bnssId_for_this_review:
                    continue

                non_singleton_usr_all_review_distribution[non_singleton_usr][revw_for_usr.getRating()] += 1.0

                date_time_for_this_usr = SIAUtil.getDateForReview(revw_for_usr)

                time_id_for_date_time = findTimeIdForDateTime(time_key_to_date_time,\
                                                              date_time_for_this_usr)
                if bnssId_for_this_review in suspicious_timestamps and \
                                time_id_for_date_time in suspicious_timestamps[bnssId_for_this_review]:
                    non_singleton_usr_suspicousness[non_singleton_usr].append(revw_for_usr)
                else:
                    non_singleton_usr_non_suspicousness[non_singleton_usr].append(
                        revw_for_usr)

        reviews_for_bnss_in_time_key = sorted([G.getReview(usrId, bnssKey) for (usrId, usr_type)
                                               in neighboring_usr_nodes],
                                              key=lambda r: SIAUtil.getDateForReview(r))

        four_grams_dict = time_wise_four_grams_dict[time_key]
        three_grams_dict = time_wise_three_grams_dict[time_key]
        two_grams_dict = time_wise_two_grams_dict[time_key]

        all_user_review_rating_distribution = time_wise_all_user_review_rating_distribution[time_key]
        singleton_review_rating_distribution = time_wise_singleton_review_rating_distribution[time_key]
        non_singleton_review_rating_distribution = time_wise_non_singleton_review_rating_distribution[time_key]

        for r in reviews_for_bnss_in_time_key:
            if readReviewsText:
                decoded_text = r.getReviewText().decode('UTF-8')
                two_grams = nltk.ngrams(nltk.word_tokenize(decoded_text), 2)
                three_grams = nltk.ngrams(nltk.word_tokenize(decoded_text), 3)
                four_grams = nltk.ngrams(nltk.word_tokenize(decoded_text), 4)

                put_grams(two_grams, two_grams_dict)
                put_grams(three_grams, three_grams_dict)
                put_grams(four_grams, four_grams_dict)

            all_user_review_rating_distribution[r.getRating()] += 1.0
            if r.getUserId() in singleton_usrs:
                singleton_review_rating_distribution[r.getRating()] += 1.0
            else:
                non_singleton_review_rating_distribution[r.getRating()] += 1.0
            date_of_review = SIAUtil.getDateForReview(r)
            time_wise_review_time_rating[r.getRating()][date_of_review] += 1.0

        time_wise_all_user_review_rating_distribution[time_key] = all_user_review_rating_distribution
        time_wise_singleton_review_rating_distribution[time_key] = singleton_review_rating_distribution
        time_wise_non_singleton_review_rating_distribution[time_key] = non_singleton_review_rating_distribution


        total_non_singleton_usrs = len(non_singleton_usrs)
        extreme_non_singleton_usrs = 0

        for usrId in non_singleton_usrs:
            rating_dist = non_singleton_usr_all_review_distribution[usrId]
            if rating_dist[2.0] == 0 and rating_dist[3.0] == 0 and rating_dist[4.0] == 0:
                extreme_non_singleton_usrs += 1
        non_extreme_non_singleton_usrs = total_non_singleton_usrs - extreme_non_singleton_usrs
        time_wise_extreme_non_singleton_usrs[time_key] = extreme_non_singleton_usrs
        time_wise_non_extreme_non_singleton_usrs[time_key] = non_extreme_non_singleton_usrs

#     if readReviewsText:
#         printNGrams(time_key_start, time_key_end, time_wise_four_grams_dict,\
#                     time_wise_three_grams_dict, time_wise_two_grams_dict)

    if doPlot:
        bnssImgFolder = os.path.join(plotDir, bnssKey + '_' + str(time_key_start)\
                                     + '_' + str(time_key_end))
        plotAllStats(time_wise_non_singleton_usr_suspicousness,\
                     time_wise_non_singleton_usr_non_suspicousness,\
                     time_wise_four_grams_dict, time_wise_three_grams_dict,\
                     time_wise_two_grams_dict,\
                     time_wise_all_user_review_rating_distribution,\
                     time_wise_singleton_review_rating_distribution,\
                     time_wise_non_singleton_review_rating_distribution,\
                     time_wise_extreme_non_singleton_usrs,\
                     time_wise_non_extreme_non_singleton_usrs,\
                     time_wise_review_time_rating,\
                     time_key_start, time_key_end, time_key_to_date_time,\
                     bnssImgFolder, statsToPlot=statsToPlot)

def performLDAOnPosNegReviews(plotDir,  bnssKey, time_key_wdw,
                              necessaryDs, num_topics=3, num_words=1):
    ctg, superGraph, time_key_to_date_time,\
     suspicious_timestamps, suspicious_timestamp_ordered = necessaryDs
    time_key_start, time_key_end = time_key_wdw
    print '------------------------ LDA ---------------------------------\n'
    for time_key in range(time_key_start, time_key_end):
        G = ctg[time_key]
        if (bnssKey, SIAUtil.PRODUCT) not in G:
            continue
        print '------------------------ Time Key', time_key, '----------------------------'
        neighboring_usr_nodes = G.neighbors((bnssKey, SIAUtil.PRODUCT))
        reviews_for_bnss_in_time_key = sorted([G.getReview(usrId, bnssKey) for (usrId, usr_type)
                                               in neighboring_usr_nodes],
                                              key=lambda r: SIAUtil.getDateForReview(r))
        if len(reviews_for_bnss_in_time_key) > 0:
            print 'All Reviews for the week - ', LDAUtil.performLDAOnReviews(reviews_for_bnss_in_time_key,
                                                                             num_topics=num_topics,
                                                                             num_words=num_words)

        pos_reviews = [revw for revw in reviews_for_bnss_in_time_key if revw.getRating() >= 4.0]
        neg_reviews = [revw for revw in reviews_for_bnss_in_time_key if revw.getRating() <= 2.0]

        if len(pos_reviews) > 0:
            print 'Positive Reviews -', LDAUtil.performLDAOnReviews(pos_reviews,
                                                                    num_topics=num_topics,
                                                                    num_words=num_words)

        if len(neg_reviews) > 0:
            print 'Negative Reviews -', LDAUtil.performLDAOnReviews(neg_reviews,
                                                                    num_topics=num_topics,
                                                                    num_words=num_words)
        print '--------------------------------------------------------------------------------\n'
    print '-------------------------------------------------------------------------------\n'


def performPhraseFilteringOnBusiness(plotDir, bnssKey, time_key_wdw, necessaryDs,
                                     phrase, similar_phrases = set()):
    ctg, superGraph, time_key_to_date_time,\
     suspicious_timestamps, suspicious_timestamp_ordered = necessaryDs
    phrases = set(similar_phrases)
    phrases.add(phrase)
    time_key_start, time_key_end = time_key_wdw
    for time_key in range(time_key_start, time_key_end):
        G = ctg[time_key]
        if (bnssKey, SIAUtil.PRODUCT) not in G:
            continue
        fdr = os.path.join(os.path.join(os.path.join(plotDir, bnssKey), str(time_key)), str(phrase))
        if not os.path.exists(fdr):
            os.makedirs(fdr)
        neighboring_usr_nodes = G.neighbors((bnssKey, SIAUtil.PRODUCT))
        reviews_for_bnss_in_time_key = sorted([G.getReview(usrId, bnssKey) for (usrId, usr_type)
                                               in neighboring_usr_nodes],
                                              key=lambda r: SIAUtil.getDateForReview(r))
    phrase_wise_rev_pn.runPhraseFilterAndSeperate(reviews_for_bnss_in_time_key, phrases, fdr)


def performWordCloudOnAllReviewsInTimeWindow(plotDir, bnssKey, time_key_wdw, necessaryDs):
    ctg, superGraph, time_key_to_date_time, suspicious_timestamps, suspicious_timestamp_ordered = necessaryDs
    time_key_start, time_key_end = time_key_wdw
    fdr = os.path.join(os.path.join(plotDir, bnssKey + '_' + str(time_key_wdw)))
    reviews = []
    for time_key in range(time_key_start, time_key_end):
        G = ctg[time_key]
        if (bnssKey, SIAUtil.PRODUCT) not in G:
            continue

        if not os.path.exists(fdr):
            os.makedirs(fdr)

        neighboring_usr_nodes = G.neighbors((bnssKey, SIAUtil.PRODUCT))
        reviews_for_bnss_in_time_key = sorted([G.getReview(usrId, bnssKey) for (usrId, usr_type)
                                               in neighboring_usr_nodes],
                                              key=lambda r: SIAUtil.getDateForReview(r))
        reviews.extend(reviews_for_bnss_in_time_key)
    phrase_wise_rev_pn.runOnAllReviews(reviews, fdr)

def sort_text_cnt(key1, key2):
    text1, review_ids1 = key1
    text2, review_ids2 = key2
    cnt1, cnt2 = len(review_ids1), len(review_ids2)
    if cnt1 > cnt2: return 1
    elif cnt1 < cnt2: return -1
    elif text1 < text2: return 1
    elif text1 > text2: return -1
    return 0

def performDuplicateCount(plotDir, bnssKey, time_key_wdw, necessaryDs, all_review_text_to_review_id):
    ctg, superGraph, time_key_to_date_time,\
     suspicious_timestamps, suspicious_timestamp_ordered = necessaryDs
    time_key_start, time_key_end = time_key_wdw
    text_to_review_ids = dict()
    bnssImgFolder = os.path.join(plotDir, bnssKey + '_' + str(time_key_start)\
                                     + '_' + str(time_key_end))
#     text_to_usr_ids = dict()
    print '----------------------------------------DUPLICATE COUNT---------------------------------------------------'

    for time_key in range(time_key_start, time_key_end):
        G = ctg[time_key]
        if (bnssKey, SIAUtil.PRODUCT) not in G:
            print 'No Reviews for Bnss in', time_key
            continue
        neighboring_usr_nodes = G.neighbors((bnssKey, SIAUtil.PRODUCT))
        reviews_for_bnss_in_time_key = sorted([G.getReview(usrId, bnssKey) for (usrId, usr_type)
                                               in neighboring_usr_nodes],
                                              key=lambda r: SIAUtil.getDateForReview(r))

        for revw in reviews_for_bnss_in_time_key:
            review_text = revw.getReviewText()
            if review_text not in text_to_review_ids:
                if review_text not in all_review_text_to_review_id:
                    print 'Cannot find review text', review_text
                    continue
                review_ids = all_review_text_to_review_id[review_text]
                if len(review_ids) > 1 and len(nltk.word_tokenize(review_text.decode('UTF-8'))) >= 2:
                    text_to_review_ids[review_text] = review_ids
    print len(text_to_review_ids), len(reviews_for_bnss_in_time_key)
    imgFolder = os.path.join(bnssImgFolder, 'text_graph')
    if not os.path.exists(imgFolder):
        os.makedirs(imgFolder)

    sorted_items = sorted(text_to_review_ids.iteritems(), cmp=sort_text_cnt, reverse=True)
    print '**********************************'
    for item in sorted_items:
        txt, review_ids = item
        print txt, len(review_ids)
    print '**********************************'

    for text in text_to_review_ids:
        review_ids = text_to_review_ids[text]
        title = text[:100].replace('/','-')
        num = 1
        while os.path.exists(os.path.join(imgFolder, title)):
            title = title + '_' + str(num)
            num += 1
        plotGraphForReviewText(review_ids, superGraph, imgFolder, title, text, time_key_to_date_time)

#     for item in sorted_items:
#         txt = item[0]
#         if txt in text_to_usr_ids:
#             print '------------------------------'
#             print txt
#             print sorted(text_to_usr_ids[txt], key = lambda (usr_id, cnt): cnt)
#             print '------------------------------'
#     print '**********************************'
    print '------------------------------------------------------------------------------------------------'


import random, numpy, datetime

def tryPlotForFB(size=40):
    non_singleton_usr_suspicousness = pickle.load(open('/media/santhosh/Data/workspace/datalab/data/stats/fk/non_singleton_usr_suspicousness.pkl'))
    bnss_to_reviews = dict()
    time_key_to_date_time = pickle.load(open('/media/santhosh/Data/workspace/datalab/data/stats/fk/time_key_to_date_time.pkl'))
    g = nx.Graph()
    bnss_nodes = set()
    usr_nodes = set()
    node_labels = dict()
#     for usrId in non_singleton_usr_suspicousness.keys():
#         for revw_for_usr in non_singleton_usr_suspicousness[usrId]:
#             bnss_id_for_revw = revw_for_usr.getBusinessID()
#             date_time_for_this_usr = SIAUtil.getDateForReview(revw_for_usr)
#
#             time_id_for_date_time = EvidenceUtil.findTimeIdForDateTime(time_key_to_date_time,\
#                                                           date_time_for_this_usr)
#
#             if bnss_id_for_revw not in bnss_to_reviews:
#                 bnss_to_reviews[bnss_id_for_revw] = []
#
#             bnss_to_reviews[bnss_id_for_revw].add((usrId, revw_for_usr.getRating(), time_id_for_date_time))
    non_singleton_usr_suspicousness_ids = [usrId for usrId in non_singleton_usr_suspicousness.keys()][:size]

    for usrId in non_singleton_usr_suspicousness_ids:
        for revw_for_usr in non_singleton_usr_suspicousness[usrId]:
            bnss_id_for_revw = revw_for_usr.getBusinessID()
            date_time_for_this_usr = SIAUtil.getDateForReview(revw_for_usr)

            time_id_for_date_time = findTimeIdForDateTime(time_key_to_date_time,\
                                                          date_time_for_this_usr)
            bnss_nodes.add(bnss_id_for_revw)
            g.add_edge(usrId, bnss_id_for_revw, {'edge': (revw_for_usr.getRating(), time_id_for_date_time)})

            node_labels[bnss_id_for_revw] = bnss_id_for_revw[:2]
            usr_nodes.add(usrId)
            node_labels[usrId] = usrId[:2]

    edge_labels=dict([((u,v,),d['edge']) for u,v,d in g.edges(data=True)])

    usr_nodes_len = len(usr_nodes)
    bnss_nodes_len = len(bnss_nodes)

    pos = dict()

    usr_node_iter = bnss_nodes_len
    for node in usr_nodes:
        pos[node] = (1, usr_node_iter)
        usr_node_iter += bnss_nodes_len

    bnss_nodes_iter = usr_nodes_len
    for node in bnss_nodes:
        pos[node] = (10, bnss_nodes_iter)
        bnss_nodes_iter += usr_nodes_len
#     X, Y = nx.algorithms.bipartite.sets(g)
#     pos = dict()
#     pos.update((n, (1, i)) for i, n in enumerate(X) ) # put nodes from X at x=1
#     pos.update((n, (100, i)) for i, n in enumerate(Y) ) # put nodes from Y at x=2

    nx.draw_networkx_nodes(g, pos,
                           nodelist=list(usr_nodes),
                           node_color='b',
                           node_size=200,
                           alpha=0.8)

    nx.draw_networkx_nodes(g, pos,
                           nodelist=list(bnss_nodes),
                           node_color='m',
                           node_size=3400,
                           alpha=0.8)

    nx.draw_networkx_edges(g, pos,
                       edgelist=[(usrId, revw_for_usr.getBusinessID())
                                 for usrId in non_singleton_usr_suspicousness_ids
                                 for revw_for_usr in non_singleton_usr_suspicousness[usrId]],
                       alpha=0.5, edge_color='red', width=1.5)


    nx.draw_networkx_labels(g, pos, labels=node_labels)
    # nx.draw_networkx_edges(g, pos, width=1.0, alpha=0.5)
#     nx.draw_networkx_edge_labels(g, pos, edge_labels=edge_labels,\
#                                  label_pos= 0.3)
    for edge_label in edge_labels:
        current_labels = {edge_label: edge_labels[edge_label]}
        nx.draw_networkx_edge_labels(g, pos, edge_labels=current_labels, font_size=50,
                                     label_pos= numpy.random.choice(numpy.arange(0.1, 0.9, 0.25)))

    plt.title('Suspicious Non Singleton User Graph', fontsize=60)
    plt.axis('off')
    fig = plt.gcf().set_size_inches(50, 50)
    PlotUtil.savePlot('/home/santhosh/logs/susicious_' + str(size) , isPdf=True)
