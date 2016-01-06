from main import AppUtil
import os
from util import SIAUtil
from util import GraphUtil
from util.GraphUtil import SuperGraph

csvFolder = '/media/santhosh/Data/workspace/datalab/data/Itunes/'
plotDir = os.path.join(os.path.join(os.path.join(csvFolder, os.pardir), 'stats'), '1')


def inspect():
    bnssKey = '319927587'
    AppUtil.findUsersInThisTimeWindow(bnssKey, (189, 192), csvFolder, plotDir)

inspect()