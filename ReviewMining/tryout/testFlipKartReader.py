import sys
from flipkart_utils import FlipkartDataReader
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print 'Usage: python -m \"tryout.testFlipkKartReader\" csvFolder'
        sys.exit()
    csvFolder = sys.argv[1]
    reader = FlipkartDataReader.FlipkartDataReader()
    reader.readData(csvFolder)
