'''
Created on Jan 8, 2016

@author: santhosh
'''
import os

import EvidenceUtil
from util.data_reader_utils.itunes_utils.ItunesDataReader import ItunesDataReader


def doGatherEvidence(csvFolder, plotDir, rdr=ItunesDataReader(), bnss_key_time_wdw_list = list()):
    evidencePlotDir = os.path.join(plotDir, 'Experiments')
    readReviewsText = False
    necessary_ds = EvidenceUtil.getNecessaryDs(csvFolder, readReviewsText=readReviewsText,
                                               rdr=rdr)
    ctg, superGraph, time_key_to_date_time,\
     suspicious_timestamps, suspicious_timestamp_ordered = necessary_ds

    bnss_phrases = dict()
    phrases = ['news', 'game', 'version', 'download', 'ign'] #284819997
    similar_phrases_dict = dict()
    bnss_phrases['284819997'] = (phrases, similar_phrases_dict)

    phrases = ['whip', 'BBG', 'version', 'download'] #319927587
    similar_phrases_dict = {'BBG': ['Big Bang Theory']}
    bnss_phrases['319927587'] = (phrases, similar_phrases_dict)

    phrases = ['funny', 'version', 'download'] #412629178
    similar_phrases_dict = dict()
    bnss_phrases['412629178'] = (phrases, similar_phrases_dict)

    phrases = ['pic', 'video', 'version', 'download'] #404593641
    similar_phrases_dict = dict()
    bnss_phrases['404593641'] = (phrases, similar_phrases_dict)

    phrases = ['pic', 'video', 'version', 'download'] #404593641
    similar_phrases_dict = dict()
    bnss_phrases['284235722'] = (phrases, similar_phrases_dict)

    all_review_text_to_review_id = dict()

    for revwId in superGraph.getReviewIds():
        revw = superGraph.getReviewFromReviewId(revwId)
        txt = revw.getReviewText()
        if txt not in all_review_text_to_review_id:
            all_review_text_to_review_id[txt] = set()
        all_review_text_to_review_id[txt].add(revw.getId())

    for bnss_key, time_key_wdw in bnss_key_time_wdw_list:
        print '-----------------', bnss_key, time_key_wdw, '-------------------------------------------'
#         EvidenceUtil.performLDAOnPosNegReviews(plotDir, bnss_key, time_key_wdw, necessary_ds,
#                                                 num_topics=5, num_words=1)
        EvidenceUtil.findStatsForEverything(evidencePlotDir,\
                                            bnss_key, time_key_wdw,\
                                            necessary_ds,\
                                            readReviewsText=readReviewsText,\
                                            doPlot=True)
#         EvidenceUtil.performDuplicateCount(evidencePlotDir, bnss_key, time_key_wdw,
#                                            necessary_ds, all_review_text_to_review_id)

#         phrases, similar_phrases_dict = bnss_phrases[bnss_key]
#
#         for phrase in phrases:
#             if phrase in similar_phrases_dict:
#                 EvidenceUtil.performPhraseFilteringOnBusiness(evidencePlotDir, bnss_key,
#                                                               time_key_wdw,
#                                                               necessary_ds, phrase,
#                                                               set(similar_phrases_dict[phrase]))
#             else:
#                 EvidenceUtil.performPhraseFilteringOnBusiness(evidencePlotDir, bnss_key, time_key_wdw,
#                                                            necessary_ds, phrase)
        print '----------------------------------------------------------------------------------------'

def printSortedReviews(csvFolder, plotDir, rdr=ItunesDataReader()):
    necessary_ds = EvidenceUtil.getNecessaryDs(csvFolder, readReviewsText=True,
                                               rdr=rdr)
    ctg, superGraph, time_key_to_date_time,\
     suspicious_timestamps, suspicious_timestamp_ordered = necessary_ds
    del ctg, time_key_to_date_time, suspicious_timestamps, suspicious_timestamp_ordered
    EvidenceUtil.sortAndPrintReviewsInfo(plotDir, superGraph)

