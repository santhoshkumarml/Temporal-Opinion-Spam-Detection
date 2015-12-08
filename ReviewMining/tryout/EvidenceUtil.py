import nltk
from nltk import ngrams

from itunes_utils.ItunesDataReader import ItunesDataReader
from tryout.AppUtil import readData
from util import GraphUtil, SIAUtil


def plotRatingDistribution(review_rating_distribution):
    import matplotlib.pyplot as plt
    fig = plt.figure(1, figsize=(6,6))
    ax = plt.axes([0.1, 0.1, 0.8, 0.8])

    # The slices will be ordered and plotted counter-clockwise.
    labels = review_rating_distribution.keys()
    fracs = review_rating_distribution.values()

    plt.pie(fracs, labels=labels,
        autopct='%1.1f%%', shadow=True, startangle=90)
    # The default startangle is 0, which would start
    # the Frogs slice on the x-axis.  With startangle=90,
    # everything is rotated counter-clockwise by 90 degrees,
    # so the plotting starts on the positive y-axis.

    plt.title('Review Rating Count', bbox={'facecolor':'0.8', 'pad':5})

    plt.show()


def findStatsForEverything(csvFolder, plotDir,  bnssKey, time_key, timeLength = '1-W',
                           rdr=ItunesDataReader(), readReviewsText=False):
    r_D = {1.0: 6.0, 2.0: 4.0, 3.0: 16.0, 4.0: 79.0, 5.0: 344.0}
    plotRatingDistribution(r_D)
    import sys
    sys.exit()

    suspicious_timestamps = dict()
    with open('/home/santhosh/out_all_features_mul_reviews') as f:
        lines = f.readlines()
        for line in lines:
            bnss_key, idx1, idx2, score = line.strip().split()
            idx1 = idx1[1:-1]
            idx2 = idx2[:-1]
            if bnss_key not in suspicious_timestamps:
                suspicious_timestamps[bnss_key] = set()
            for idx in range(int(idx1), int(idx2)):
                suspicious_timestamps[bnss_key].add(idx)

    bnssIdToBusinessDict, reviewIdToReviewsDict, usrIdToUserDict = readData(csvFolder,
                                                                            readReviewsText=readReviewsText, rdr=rdr)
    ctg = GraphUtil.createTemporalGraph(usrIdToUserDict,
                                                      bnssIdToBusinessDict,
                                                      reviewIdToReviewsDict,
                                                      timeLength)
    superGraph = GraphUtil.createSuperGraph(usrIdToUserDict, bnssIdToBusinessDict,
                                            reviewIdToReviewsDict, timeLength)

    G = ctg[time_key]

    neighboring_usr_nodes = G.neighbors((bnssKey, SIAUtil.PRODUCT))
    all_usrs = set([usrId for usrId, usr_type in neighboring_usr_nodes])
    singleton_usrs = set([usrId for usrId, usr_type in neighboring_usr_nodes
                  if len(superGraph.neighbors((usrId, usr_type))) == 1])
    non_singleton_usrs = all_usrs - singleton_usrs

    non_singleton_usr_suspicousness = dict()
    total_reviews_for_non_singleton_usr = dict()
    review_distribution_for_non_singleton_usr = dict()
    time_key_to_date_time = dict()

    for time_key in ctg.keys():
        d = ctg[time_key].getDateTime()
        time_key_to_date_time[time_key] = d


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

    del neighboring_usr_nodes, all_usrs, non_singleton_usrs,\
        time_key_to_date_time, suspicious_timestamps, superGraph, ctg

    four_games_dict = dict()
    three_grams_dict = dict()
    two_grams_dict = dict()

    def put_grams(grams, grams_dict):
        for gram in grams:
            if gram not in grams_dict:
                grams_dict[gram] = 0.0
            grams_dict[gram] += 1.0

    review_time_rating = dict()
    review_rating_distribution = {float(key): 0.0 for key in range(1, 6)}
    singleton_review_rating_distribution = {float(key): 0.0 for key in range(1, 6)}

    for r in reviews_for_bnss_in_time_key:
        if readReviewsText:
            decoded_text = r.getReviewText().decode('UTF-8')
            two_grams = ngrams(nltk.word_tokenize(decoded_text), 2)
            three_grams = ngrams(nltk.word_tokenize(decoded_text), 3)
            four_grams = ngrams(nltk.word_tokenize(decoded_text), 4)

            put_grams(two_grams, two_grams_dict)
            put_grams(three_grams, three_grams_dict)
            put_grams(four_grams, four_games_dict)

        review_rating_distribution[r.getRating()] += 1.0
        if r.getUserId() in singleton_usrs:
            singleton_review_rating_distribution[r.getRating()] += 1.0
        date_of_review = SIAUtil.getDateForReview(r)
        if date_of_review not in review_time_rating:
            review_time_rating[date_of_review][r.getRating()] = {float(key): dict() for key in range(1, 6)}
        review_time_rating[date_of_review][r.getRating()] += 1.0

    print 'Review Rating Distribution:'
    print review_rating_distribution
    print 'Review Time Rating:'
    print review_time_rating
    print 'Singleton Distribution:'
    print singleton_review_rating_distribution
    print 'Non Singleton User Suspiciousness:'
    print sorted(non_singleton_usr_suspicousness.iteritems(),
                 key=lambda (usrId, count): count, reverse=True)
    print 'Review Distribution for Non Singleton User:'
    print sorted(review_distribution_for_non_singleton_usr.iteritems(),
                 key=lambda (usrId, distribution): total_reviews_for_non_singleton_usr[usrId], reverse=True)
    print 'Total Reviews for Non Singleton User Suspiciousness:'
    print sorted(total_reviews_for_non_singleton_usr.iteritems(), key=lambda (usrId, count) : count, reverse=True)
    if readReviewsText:
        print 'Two Grams'
        print sorted(two_grams_dict.iteritems(), key=lambda (gram, count) : count, reverse=True)
        print 'Three Grams'
        print sorted(three_grams_dict.iteritems(), key=lambda (gram, count) : count, reverse=True)
        print 'Four Grams'
        print sorted(four_games_dict.iteritems(), key=lambda (gram, count) : count, reverse=True)