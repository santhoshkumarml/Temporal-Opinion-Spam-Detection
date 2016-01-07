'''
Created on Jan 6, 2016

@author: santhosh
'''
from main import AppUtil
from datetime import datetime
import sys, os
import matplotlib.pyplot as plt
import numpy
from util.data_reader_utils.anon_ecomm_utils.AnonEcommDataReader import AnonEcommDataReader


def tryPlotting():
    fig, axarr = plt.subplots(9, 2, figsize=(20, 20))
    for x in range(9):
        for y in range(2):
            ax = axarr[x][y]
            ax.plot(numpy.random.normal((2*x)+y, 0.2, 150), color='g')
            if y == 1:
                ax.set_xticklabels([])
            position = ax.get_position()
            left = position.x0
            top = position.y0
            right = position.x0 + position.width
            bottom = position.y0 + position.height

            ax.text(0.5*(left + right), 0.5*(bottom + top), 'text',
                            horizontalalignment='center',
                            verticalalignment='center',
                            fontsize=10, color='red',
                            transform=ax.transAxes)


    fig.subplots_adjust(wspace=0.05, hspace=1)
    plt.show()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print 'Usage: python -m \"tryout.test\" csvFolder'
        sys.exit()
    csvFolder = sys.argv[1]

    plotDir = os.path.join(os.path.join(os.path.join(csvFolder, os.pardir), 'stats'), 'fk')

    bnss_set1 = set(['8edd789d64c7279592057487ff5bb264', 'd2c9f8c737d5d402593917a618d47821',
                    'f04bc4093557a51a3fdde40ef92464c9', 'beaa44a68be8aa0858cbe3e83a23964a',
                    'dc9d0a3389e58f134ff9dc0435e1a962', 'fb57b2749835facf54d9c73f0d9a8d4c']) #fb57b2749835facf54d9c73f0d9a8d4c, 8edd789d64c7279592057487ff5bb26

    bnss_set2 = set(['8256464cc62ac60780732f469c31ed93', 'a81540b49865cac9dc0b4c4a069e2f65',
                    'e4bbdc5b36c01ec46070ead21fd4ef0b', 'cb21ab81ffc3230896eac3538751d79c',
                    'c116413510bda494fb021f4b7dcdab13', 'b030c6c50bd7ce01135fffa638e74a9b',
                    '6158e8725c8f9fd9dec469088512cd6a', '112262aec34dc24c5b2e9bf91346a5ed',
                    'ebc30981f0f18aeaee44c403e459cf01',
                    'b030c6c50bd7ce01135fffa638e74a9b', '6158e8725c8f9fd9dec469088512cd6a',
                    'fafc1f6a28f03bf1dc8b655c9706e184'
                    'a9856cb97ebd363a0581d08f27f8b379'])#a9856cb97ebd363a0581d08f27f8b379
    bnss_set = bnss_set1 | bnss_set2

    rdr = AnonEcommDataReader()
    bnssIdToBusinessDict, reviewIdToReviewsDict, usrIdToUserDict = AppUtil.readData(csvFolder,
                                                                                    readReviewsText=True,
                                                                                    rdr=rdr)
    del bnssIdToBusinessDict, usrIdToUserDict
    revwLogFolder = os.path.join(plotDir, 'bnss_revw')

    if not os.path.exists(revwLogFolder):
        os.makedirs(revwLogFolder)

    for revwId in reviewIdToReviewsDict.keys():
        revw = reviewIdToReviewsDict[revwId]
        if revw.getBusinessID() in bnss_set and revw.getReviewText() != '':
            with open(os.path.join(revwLogFolder, revw.getBusinessID()), 'a') as f:
                f.write('----------------------------------------------------------\n')
                f.write(revw.toString())
                f.write('\n')
                f.write('----------------------------------------------------------\n')

#     currentDateTime = datetime.now().strftime('%d-%b--%H:%M')
#     bnss_key_time_wdw_list = [('284235722', (140, 142)),
#                               ('284819997', (150, 152)),
#                               ('319927587', (120, 122)),
#                               ('284819997', (166, 171)), ('284819997', (173, 178)),
#                               ('284819997', (180, 185)), ('284819997', (187, 192)),
#                               ('319927587', (189, 194)), ('404593641', (158, 163)),
#                               ('412629178', (148, 153)), ('284235722', (147,152))]
#     AppUtil.doGatherEvidence(csvFolder, plotDir, bnss_key_time_wdw_list=bnss_key_time_wdw_list)

