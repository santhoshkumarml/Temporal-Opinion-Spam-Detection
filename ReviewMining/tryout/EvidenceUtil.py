import collections
import datetime
import os

import matplotlib.pyplot as plt
import networkx as nx
import nltk
import numpy

import AppUtil
from itunes_utils.ItunesDataReader import ItunesDataReader
from util import GraphUtil, SIAUtil


def plotSuspiciousNessGraph(non_singleton_usr_suspicousness, imgFolder,
                            title='Suspicious Non Singleton User'):
    imgFile = os.path.join(imgFolder, title + '.png')

    g = nx.Graph()
    g.add_edge(2, 3, weight=1)

    pos = nx.spring_layout(g)

    edge_labels = {(u, v): d['weight'] for u, v, d in g.edges(data=True)}

    nx.draw_networkx_nodes(g, pos, node_size=700)
    nx.draw_networkx_edges(g, pos)
    nx.draw_networkx_labels(g, pos)
    nx.draw_networkx_edge_labels(g, pos, edge_labels=edge_labels)

    plt.title(title)
    plt.axis('off')
    plt.savefig(imgFile)
    plt.close()


def plotRatingDistribution(review_rating_distribution, imgFolder,
                           title='Rating Distribution'):
    fig = plt.figure(figsize=(10, 6))
    ax = plt.axes([0.1, 0.1, 0.8, 0.8])
    imgFile = os.path.join(imgFolder, title + '.png')
    labels = review_rating_distribution.keys()
    fracs = review_rating_distribution.values()

    ax.pie(fracs, labels=labels,
        autopct='%1.0f%%', shadow=False, startangle=90)
    plt.title(title, bbox={'facecolor': '0.8', 'pad': 5})
    plt.legend()
    plt.savefig(imgFile, bbox_inches='tight')
    plt.close()


def plotExtremityForNonSingletonUsr(extreme_usrs, non_extreme_usrs, imgFolder,
                                    title='Extremity of Non SingletonUsr'):
    fig = plt.figure(figsize=(10, 6))
    ax = fig.add_subplot(1, 1, 1)
    width = 0.20
    imgFile = os.path.join(imgFolder, title + '.png')
    x_labels = ['Extreme Users', 'Non Extreme Users']
    p_extreme = ax.bar(0, extreme_usrs, width, color='r')
    p_non_extreme = ax.bar(0.5, non_extreme_usrs, width, color='b')

    plt.ylabel('Count')
    plt.title(title)
    plt.xticks([0.10, 0.60], x_labels)
    plt.legend()
    plt.savefig(imgFile, bbox_inches='tight')
    plt.close()


def plotReviewTimeRating(review_time_rating, imgFolder, title='Time Wise Rating Count'):
    fig = plt.figure(figsize=(10, 6))
    ax = fig.add_subplot(1, 1, 1)
    imgFile = os.path.join(imgFolder, title + '.png')
    colors = ['y', 'c', 'm', 'b', 'r']
    ind = numpy.arange(0, 7)
    width = 0.35
    x_labels = [d.strftime('%m/%d/%Y') for d in sorted(review_time_rating[1.0].keys())]
    pS = []
    btm = None
    colr = 0
    for rating_key in sorted(review_time_rating.keys()):
        val = review_time_rating[rating_key]
        od = collections.OrderedDict(sorted(val.items()))
        val = od.values()
        if not btm:
            p = ax.bar(ind,val, width, color=colors[colr])
        else:
            p = ax.bar(ind, val, width, color=colors[colr], bottom=btm)
        btm = val
        colr += 1
        pS.append(p)

    plt.ylabel(title)
    plt.title(title)
    plt.xticks(ind + width/2., x_labels)
    plt.legend([p[0] for p in pS], range(1, 6))
    plt.savefig(imgFile, bbox_inches='tight')
    plt.close()


def getNecessaryDs(csvFolder, rdr=ItunesDataReader(), readReviewsText=False, timeLength='1-W'):
    suspicious_timestamps = dict()
    suspicious_timestamp_ordered = list()
    with open('/home/santhosh/out_all_features_mul_reviews') as f:
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


def findStatsForEverything(plotDir,  bnssKey, time_key, necessaryDs, readReviewsText=False, doPlot=False):
    ctg, superGraph, time_key_to_date_time, suspicious_timestamps, suspicious_timestamp_ordered = necessaryDs

    G = ctg[time_key]

    neighboring_usr_nodes = G.neighbors((bnssKey, SIAUtil.PRODUCT))
    all_usrs = set([usrId for usrId, usr_type in neighboring_usr_nodes])
    singleton_usrs = set([usrId for usrId, usr_type in neighboring_usr_nodes
                  if len(superGraph.neighbors((usrId, usr_type))) == 1])
    non_singleton_usrs = all_usrs - singleton_usrs

    non_singleton_usr_suspicousness = dict()
    total_reviews_for_non_singleton_usr = dict()
    review_distribution_for_non_singleton_usr = dict()

    d_start = time_key_to_date_time[time_key]

    for non_singleton_usr in non_singleton_usrs:
        reviews_for_this_usr = sorted([superGraph.getReview(non_singleton_usr, bnssId) for (bnssId, bnss_type)
                                       in superGraph.neighbors((non_singleton_usr, SIAUtil.USER))])
        total_reviews_for_non_singleton_usr[non_singleton_usr] = len(reviews_for_this_usr)
        review_distribution_for_non_singleton_usr[non_singleton_usr] = {float(key): 0.0 for key in range(1, 6)}

        if non_singleton_usr not in non_singleton_usr_suspicousness:
            non_singleton_usr_suspicousness[non_singleton_usr] = 0.0

        for revw_for_usr in reviews_for_this_usr:
            bnssId_for_this_review = revw_for_usr.getBusinessID()
            review_distribution_for_non_singleton_usr[non_singleton_usr][revw_for_usr.getRating()] += 1.0
            if bnssId_for_this_review not in suspicious_timestamps:
                continue
            date_time_for_this_usr = SIAUtil.getDateForReview(revw_for_usr)
            time_id_for_date_time = -1
            for time_key in time_key_to_date_time.keys():
                if date_time_for_this_usr < time_key_to_date_time[time_key].date():
                    time_id_for_date_time = time_key
                    break
            if time_id_for_date_time in suspicious_timestamps[bnssId_for_this_review]:
                non_singleton_usr_suspicousness[non_singleton_usr] += 1.0

    reviews_for_bnss_in_time_key = sorted([G.getReview(usrId, bnssKey) for (usrId, usr_type)
                                           in neighboring_usr_nodes],
                                          key=lambda r: SIAUtil.getDateForReview(r))

    del neighboring_usr_nodes, all_usrs, non_singleton_usrs

    four_games_dict = dict()
    three_grams_dict = dict()
    two_grams_dict = dict()

    def put_grams(grams, grams_dict):
        for gram in grams:
            if gram not in grams_dict:
                grams_dict[gram] = 0.0
            grams_dict[gram] += 1.0

    review_time_rating = {float(key): {
        (d_start+datetime.timedelta(days=i)).date(): 0.0 for i in range(0, 7)}
                          for key in range(1, 6)}
    review_rating_distribution = {float(key): 0.0 for key in range(1, 6)}
    singleton_review_rating_distribution = {float(key): 0.0 for key in range(1, 6)}

    for r in reviews_for_bnss_in_time_key:
        if readReviewsText:
            decoded_text = r.getReviewText().decode('UTF-8')
            two_grams = nltk.ngrams(nltk.word_tokenize(decoded_text), 2)
            three_grams = nltk.ngrams(nltk.word_tokenize(decoded_text), 3)
            four_grams = nltk.ngrams(nltk.word_tokenize(decoded_text), 4)

            put_grams(two_grams, two_grams_dict)
            put_grams(three_grams, three_grams_dict)
            put_grams(four_grams, four_games_dict)

        review_rating_distribution[r.getRating()] += 1.0
        if r.getUserId() in singleton_usrs:
            singleton_review_rating_distribution[r.getRating()] += 1.0
        date_of_review = SIAUtil.getDateForReview(r)
        review_time_rating[r.getRating()][date_of_review] += 1.0

    print 'Non Singleton User Suspiciousness:'
    print sorted(non_singleton_usr_suspicousness.iteritems(),
                 key=lambda (usrId, count): count, reverse=True)
    print 'Review Distribution for Non Singleton User:'
    print sorted(review_distribution_for_non_singleton_usr.iteritems(),
                 key=lambda (usrId, distribution): total_reviews_for_non_singleton_usr[usrId], reverse=True)

    total_non_singleton_usrs = len(review_distribution_for_non_singleton_usr.keys())
    extreme_non_singleton_usrs = 0
    non_extreme_non_singleton_usrs = 0

    for usrId in review_distribution_for_non_singleton_usr.keys():
        rating_dist = review_distribution_for_non_singleton_usr[usrId]
        if rating_dist[2.0] == 0 and rating_dist[3.0] == 0 and rating_dist[4.0] == 0:
            extreme_non_singleton_usrs += 1
    non_extreme_non_singleton_usrs = total_non_singleton_usrs - extreme_non_singleton_usrs

    print 'Total Reviews for Non Singleton User Suspiciousness:'
    print sorted(total_reviews_for_non_singleton_usr.iteritems(), key=lambda (usrId, count): count, reverse=True)

    if readReviewsText:
        print 'Two Grams'
        print sorted(two_grams_dict.iteritems(), key=lambda (gram, count): count, reverse=True)
        print 'Three Grams'
        print sorted(three_grams_dict.iteritems(), key=lambda (gram, count): count, reverse=True)
        print 'Four Grams'
        print sorted(four_games_dict.iteritems(), key=lambda (gram, count): count, reverse=True)

    if doPlot:
        imgFolder = os.path.join(plotDir, bnssKey + '_' + str(time_key))
        if not os.path.exists(imgFolder):
            os.mkdir(imgFolder)
        plotRatingDistribution(review_rating_distribution, imgFolder, title='All Review Rating Count')
        plotReviewTimeRating(review_time_rating, imgFolder)
        plotRatingDistribution(singleton_review_rating_distribution, imgFolder, title='Singleton Review Rating Count')
        plotExtremityForNonSingletonUsr(extreme_non_singleton_usrs, non_extreme_non_singleton_usrs, imgFolder)
