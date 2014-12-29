import util.dataReader as dataReader
from datetime import datetime
import sys
from util import SIAUtil
inputFileName = sys.argv[1]
beforeGraphPopulationTime = datetime.now()
(parentUserIdToUserDict,parentBusinessIdToBusinessDict,parent_reviews)\
 = dataReader.parseAndCreateObjects(inputFileName)
cross_time_graphs = SIAUtil.createTimeBasedGraph(parentUserIdToUserDict,\
                                                  parentBusinessIdToBusinessDict, parent_reviews, '1-M', False)
