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

    all_review_text_to_review_id = dict()

    for revwId in superGraph.getReviewIds():
        revw = superGraph.getReviewFromReviewId(revwId)
        txt = revw.getReviewText()
        if txt not in all_review_text_to_review_id:
            all_review_text_to_review_id[txt] = set()
        all_review_text_to_review_id[txt].add(revw.getId())

    for bnss_key, time_key_wdw in bnss_key_time_wdw_list:
        print '-----------------', bnss_key, time_key_wdw, '-------------------------------------------'
#         [EvidenceUtil.RATING_DISTRIBUTION, EvidenceUtil.TIME_WISE_RATING, EvidenceUtil.SUSPICIOUSNESS_GRAPH, EvidenceUtil.EXTREMITY_OF_NON_SINGLETON_USERS]
        EvidenceUtil.findStatsForEverything(evidencePlotDir,\
                                            bnss_key, time_key_wdw,\
                                            necessary_ds,\
                                            readReviewsText=readReviewsText,\
                                            doPlot=True,
                                            statsToPlot = [EvidenceUtil.RATING_DISTRIBUTION])
#         EvidenceUtil.performWordCloudOnAllReviewsInTimeWindow(evidencePlotDir, bnss_key, time_key_wdw, necessary_ds)

        print '----------------------------------------------------------------------------------------'

def printSortedReviews(csvFolder, plotDir, rdr=ItunesDataReader()):
    necessary_ds = EvidenceUtil.getNecessaryDs(csvFolder, readReviewsText=True,
                                               rdr=rdr)
    ctg, superGraph, time_key_to_date_time,\
     suspicious_timestamps, suspicious_timestamp_ordered = necessary_ds
    del ctg, time_key_to_date_time, suspicious_timestamps, suspicious_timestamp_ordered
    EvidenceUtil.sortAndPrintReviewsInfo(plotDir, superGraph)

