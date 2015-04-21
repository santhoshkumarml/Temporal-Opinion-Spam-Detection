__author__ = 'santhosh'

import numpy
import matplotlib.pyplot as plt

CHPT1 = 'INCREASE_AND_DECREASE'
CHPT2 = 'INCREASE_AND_INCREASE'
OUTLIER1 = 'OUTLIER_INCREASE'
OUTLIER2 = 'OUTLIER_DECREASE'

def plotDataAndChanges(data, scores=[], changes=[]):
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)
    ax.plot(range(len(data)), data, 'b')

    if len(scores) > 0:
        ax2 = ax.twinx()
        ax2.plot(range(len(data)), data,'r')
    for idx in changes:
        ax.axvline(x=idx, linewidth=2, color='r')

    plt.show()


def makeNormalData(mean=0.7, varaince =0.05, data_size=200, induced_outlier_or_chpts=[], outlier_types = []):
    data = numpy.random.normal(mean, varaince, data_size)
    assert len(outlier_types) == len(induced_outlier_or_chpts)
