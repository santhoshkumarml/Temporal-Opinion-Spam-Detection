from yelp_utils import YelpDataReader
from datetime import datetime
import sys


inputFileName = sys.argv[1]
beforeDataReadTime = datetime.now()
    
rdr = YelpDataReader()
(usrIdToUserDict,bnssIdToBusinessDict,reviewIdToReviewsDict) = rdr.readData(inputFileName)
    
afterDataReadTime = datetime.now()
    
print 'TimeTaken for Reading data:',afterDataReadTime-beforeDataReadTime