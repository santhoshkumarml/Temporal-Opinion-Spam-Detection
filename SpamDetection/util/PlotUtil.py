'''
Created on Jan 10, 2015

@author: Santhosh
'''

from matplotlib.backends.backend_pdf import PdfPages
import os, math

from anomaly_detection import AnomalyDetector
import matplotlib.pyplot as plt
from util import StatConstants


def plotTimeSeries(ax, x, y, label):
    ax.plot(x, y, 'g', linewidth=1.5, label=label)

def plotOutlierScores(ax, x, y):
    ax.plot(x, y, 'r', label='Outlier Scores', linewidth=1.5)

def plotOutlierLine(ax, x):
    ax.axvline(x=x, color='b', linewidth=1.5)

def savePlot(imgFileName, isPdf=False):
    if isPdf:
        imgFileName = imgFileName + ".pdf"
        with PdfPages(imgFileName) as pdf:
            pdf.savefig()
    else:
        imgFileName = imgFileName + ".png"
        plt.savefig(imgFileName)
    plt.close()


def setFontSizeForAxes(ax, font_size=13):
    for item in ([ax.title, ax.xaxis.label, ax.yaxis.label]
                                  + ax.get_xticklabels() + ax.get_yticklabels()):
        item.set_fontsize(font_size)

def plotLabelAsText(ax, txt):
    position = ax.get_position()
    left = position.x0
    right = position.x0 + position.width
    top = position.y0
    bottom = position.y0 + position.height

    ax.text(0.5*(left + right), 0.5*(bottom + top), txt,
                    horizontalalignment='center',
                    verticalalignment='center',
                    fontsize=13, color='black',
                    transform=ax.transAxes)

def plotMeasuresForBnss(statistics_for_bnss, chPtsOutliersForBnss, inputDir, toBeUsedMeasures,
                         avg_idxs, timeLength = '1-M'):
    plot, step = 0, 10

    toBeUsedMeasures = [measure for measure in StatConstants.MEASURE_PRIORITY if measure in toBeUsedMeasures]
    max_algo_len = max([len(StatConstants.MEASURES_CHANGE_DETECTION_ALGO[measure_key])\
                         for measure_key in toBeUsedMeasures ])

    firstTimeKey = statistics_for_bnss[StatConstants.FIRST_TIME_KEY]
    lastTimeKey = statistics_for_bnss[StatConstants.LAST_TIME_KEY]
    firstDimensionValues = range(firstTimeKey, lastTimeKey+1)
    xticks = range(firstTimeKey, lastTimeKey+1, step)

    imgFile = os.path.join(inputDir, statistics_for_bnss[StatConstants.BNSS_ID]+"_stat") + '.pdf'

    fig, axarr = plt.subplots(len(toBeUsedMeasures), max_algo_len, figsize=(17, 13), sharex='col', sharey='row')

    for measure_key in toBeUsedMeasures:
        if measure_key not in statistics_for_bnss or measure_key == StatConstants.NO_OF_REVIEWS:
            continue
        data = statistics_for_bnss[measure_key][firstTimeKey:lastTimeKey+1]

        if chPtsOutliersForBnss:
            algoList = chPtsOutliersForBnss[measure_key].keys()

            if len(algoList) != max_algo_len and len(algoList) == 1:
                algoList = [algoList[0] for algo_iter in range(max_algo_len)]

            for algo_indx in range(len(algoList)):
                algo = algoList[algo_indx]
                ax1 = axarr[plot][algo_indx]

                if plot == 0:
                    if algo_indx == 0:
                        ax1.set_title('Global')
                    else:
                        ax1.set_title('Local')

                if plot == len(toBeUsedMeasures) - 1:
                    ax1.set_xlabel('Week')

                ax1.set_xlim(firstTimeKey, lastTimeKey)
                ax1.set_xticks(xticks)


                setFontSizeForAxes(ax1)
                plotLabelAsText(ax1, measure_key)

                if measure_key == StatConstants.AVERAGE_RATING:
                    ax1.set_ylim((1, 5))
                    ax1.set_yticks(range(1, 6))

                modified_data = data
                if measure_key in [StatConstants.NON_CUM_NO_OF_REVIEWS,
                                   StatConstants.NO_OF_POSITIVE_REVIEWS,
                                   StatConstants.NO_OF_NEGATIVE_REVIEWS]:
                    modified_data = [d+1 for d in data]
                    ax1.set_yscale('log')

                plotTimeSeries(ax1, firstDimensionValues, modified_data, measure_key)

                chOutlierIdxs, chPtsOutlierScores = chPtsOutliersForBnss[measure_key][algo]

                if len(chPtsOutlierScores) > 0:
                    max_score = -float('inf')
                    min_score = float('inf')

                    for a in algoList:
                        idxs, scs = chPtsOutliersForBnss[measure_key][a]
                        if len(scs) > 0:
                            max_score = max((max_score, max(scs)))
                            min_score = min((min_score, min(scs)))

                    if measure_key in [StatConstants.NON_CUM_NO_OF_REVIEWS,
                                       StatConstants.NO_OF_POSITIVE_REVIEWS,
                                       StatConstants.NO_OF_NEGATIVE_REVIEWS]:
                        max_score += 1
                        min_score += 1

                    ax2 = ax1.twinx()
                    ax2.set_ylim((min_score, max_score + 0.01))
                    setFontSizeForAxes(ax2)

                    if algo_indx == 0:
                        ax2.set_yticklabels([])

                    scores = chPtsOutlierScores
                    if len(scores) > 0:
                        if algo == StatConstants.LOCAL_AR:
                            for idx in sorted(avg_idxs):
                                idx1, idx2 = AnomalyDetector.getRangeIdxs(idx)
                                x = []
                                plot_scores = []
                                for indx in range(idx1, idx2+1):
                                    if indx >= len(scores):
                                        continue
                                    x.append(firstTimeKey+indx)
                                    if measure_key in [StatConstants.NON_CUM_NO_OF_REVIEWS,
                                       StatConstants.NO_OF_POSITIVE_REVIEWS, StatConstants.NO_OF_NEGATIVE_REVIEWS]:
                                        plot_scores.append(scores[indx]+1)
                                        if algo_indx == 1:
                                            ax2.set_yscale('log')
                                    else:
                                        plot_scores.append(scores[indx])
                                plotOutlierScores(ax2, x, plot_scores)
                        else:
                            if measure_key in [StatConstants.NON_CUM_NO_OF_REVIEWS,
                                       StatConstants.NO_OF_POSITIVE_REVIEWS,
                                       StatConstants.NO_OF_NEGATIVE_REVIEWS]:
                                scores = chPtsOutlierScores
                                scores = [scores[indx]+1 for indx in range(len(scores))]

                                if algo_indx == 1:
                                    ax2.set_yscale('log')

                                plotOutlierScores(ax2, range(firstTimeKey, firstTimeKey + len(scores)), scores)
                            else:
                                plotOutlierScores(ax2, range(firstTimeKey, firstTimeKey + len(chPtsOutlierScores)), chPtsOutlierScores)

                if measure_key not in StatConstants.MEASURE_LEAD_SIGNALS:
                    for idx in sorted(avg_idxs):
                        idx1, idx2 = AnomalyDetector.getRangeIdxs(idx)
                        outlier_idxs = [outlier_idx for outlier_idx in chOutlierIdxs if
                                        outlier_idx < idx2 and idx1 <= outlier_idx < len(chPtsOutlierScores)]
                        if len(outlier_idxs) > 0:
                            outlier_idx = min(outlier_idxs, key= lambda outlier_idx : math.fabs(idx-outlier_idx))
                            plotOutlierLine(ax1, firstDimensionValues[outlier_idx])
                else:
                    for idx in chOutlierIdxs:
                        plotOutlierLine(ax1, firstDimensionValues[idx])


        plot += 1

    fig.subplots_adjust(hspace=0.17, wspace=0.030)

    print statistics_for_bnss[StatConstants.BNSS_ID] + " stats are logged to " + imgFile

    savePlot(imgFile)