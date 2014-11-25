YELP_COM_URL = 'http://www.yelp.com'
__author__ = 'S.R'
__date__ = 'Nov 24th, 2014'

from BeautifulSoup import BeautifulSoup
import urllib2
import argparse
import re

def extractText(tag, default=None, verbose=False, attrs={}):
    try:
        if False in [True if(re.compile(attrs[key]).match(tag[key])) else False for key in attrs.keys()]:
            return default
        else:
            return tag.getText()
    except Exception, e:
        if verbose: print 'Extracting ' + attrs + 'failed.', str(e)
    return default

def extractTagAttribute(tag, default=None, verbose=False, property='content', attrs={}):
    try:
        if False in [True if(re.compile(attrs[key]).match(tag[key])) else False for key in attrs.keys()]:
            return default
        else:
            return tag[property]
    except Exception, e:
        if verbose: print 'Extracting ' + attrs + 'failed.', str(e)
    return default

def crawl_page(url, verbose=False):
    soup = BeautifulSoup(urllib2.urlopen(url).read())
    for tag in soup.findAll('div', {'class':'biz-main-info embossed-text-white'}):
        for subtag in tag.findAll('meta', {'itemprop':'ratingValue'}):
            return float(extractTagAttribute(subtag, -1, verbose))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Extracts details of yelp restaurant')
    parser.add_argument('-f', '--file', type=str, help='Enter file')
    args = parser.parse_args()

    with open(args.file, mode='r') as f:
        for line in f:
            if line.startswith("B="):
                B=[] #TMP HOLDER
                exec(line)
                B[4] = crawl_page(B[4])
                print 'B=', B
            else:
                print line