__author__ = 'santhosh'

import numpy
import matplotlib.pyplot as plt

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


def makeNormalData(mean=0.7, varaince =0.05,data_size = 200,outierOrChGap = 10, chptSize = 5):
    data = numpy.random.normal(mean, varaince, data_size)
    plotDataAndChanges(data)
