YELP_COM_URL = 'http://www.yelp.com'
__author__ = 'S.R'
__date__ = 'Oct 27th, 2014'

import argparse
import random
import re
import sys
import time
import urllib2

from BeautifulSoup import BeautifulSoup


get_yelp_page = \
    lambda zipcode, page_num: \
        'http://www.yelp.com/search?find_desc=&find_loc={0}' \
        '&ns=1#cflt=restaurants&start={1}'.format(zipcode, page_num)

ZIP_URL = sys.argv[1]
FIELD_DELIM = u'###'
LISTING_DELIM = u'((('

def get_zips():
    """
    """
    f = open(ZIP_URL, 'r+')
    zips = [int(zz.strip()) for zz in f.read().split('\n') if zz.strip() ]
    f.close()
    return zips

def getSoupsForZip(zipcode, max_count=1):
    try:
        soups = []
        page_num = 0
        count = -1
        while True:
            page_url = get_yelp_page(zipcode, page_num)
            print page_url
            soup = BeautifulSoup(urllib2.urlopen(page_url).read())
            if soup:
                soups.append(soup)
            page_num = page_num + 11
            #print soup
            if count < 0:
                count = 11 * min(max_count, int(re.findall(r'\d+', str(soup.findAll('div', attrs={'class':re.compile(r'page-of-pages')})[0]))[1]))
            if count <= page_num:
                break
        return soups
    except Exception, e:
        print str(e)
        return None

def extractText(tag, default=None, verbose=False, attrs={}):
    try:
        if False in [True if(re.compile(attrs[time_key]).match(tag[time_key])) else False for time_key in attrs.keys()]:
            return default
        else:
            return tag.getText()
    except Exception, e:
        if verbose: print 'Extracting ' + attrs + 'failed.', str(e)
    return default

def extractTagAttribute(tag, default=None, verbose=False, property='content', attrs={}):
    try:
        if False in [True if(re.compile(attrs[time_key]).match(tag[time_key])) else False for time_key in attrs.keys()]:
            return default
        else:
            return tag[property]
    except Exception, e:
        if verbose: print 'Extracting ' + attrs + 'failed.', str(e)
    return default


def getReviews(seenDict, tag, verbose):
    ret = []
    for review in tag.findAll('div'):
        reviewID = extractTagAttribute(review, None, verbose, 'data-review-id', attrs={'class': '^review'})
        if reviewID != None and reviewID not in seenDict.keys():
            for i in review.findAll('i'):
                rating = extractTagAttribute(i, None, verbose, 'title', attrs={'class': '^star-img'})
                if rating:
                    rating = re.findall(r'\d+.?\d+', str(rating))[0]
                    seenDict[reviewID] = rating
                    for d in review.findAll('span'):
                        date = extractText(d, None, verbose, attrs={'class': '^rating-qualifier'})
                        if date:
                            date = re.findall(r'\d+\/\d+\/\d+', str(date))[0]
                            mediaAvatar = review.find('div', attrs={'class': 'media-avatar'})
                            mediaStory = review.find('div', attrs={'class': 'media-story'})
                            reviewContent = review.find('div', attrs={'class': 'review-content'})
                            imgSrc =  extractTagAttribute(mediaAvatar.find('img'), None, verbose, 'src')
                            username = extractText(mediaStory.find('li', attrs={'class': 'user-name'}).find(['a','span']), None, verbose)
                            userLocation = extractText(mediaStory.find('li', attrs={'class': 'user-location'}).find('b'), None, verbose)
                            userFriendCount = extractText(mediaStory.find('li', attrs={'class': 'friend-count'}).find('b'), None, verbose)
                            userReviewCount = extractText(mediaStory.find('li', attrs={'class': 'review-count'}).find('b'), None, verbose)
                            assert username and userLocation and userFriendCount and userReviewCount
                            userId = (username, imgSrc, userLocation, userFriendCount, userReviewCount)
                            for p in reviewContent.findAll('p'):
                                reviewText = extractText(p, '', verbose, attrs={'class': '^review_comment'})
                                if reviewText:
                                    reviewText = reviewText.replace('\n', '')
                                    ret.append((reviewID, userId, username, rating, date, reviewText))
    return ret


def crawl_page(zipcode, verbose=False):
    soups = getSoupsForZip(zipcode)
    for zipPage in soups:
        for rl in zipPage.findAll('a', attrs={'class':re.compile('^biz-name')}):
            restaurantMainPage = YELP_COM_URL + re.findall('href=[\'"]?([^\'" >]+)', str(rl))[0]
            #print restaurantMainPage
            soup = BeautifulSoup(urllib2.urlopen(restaurantMainPage).read())
            nrsoup = BeautifulSoup(urllib2.urlopen(restaurantMainPage.replace('biz','not_recommended_reviews')).read())

            attributeTags = soup.findAll()
            nrTags = nrsoup.findAll('li')

            type= 'business'
            business_id = 'UNKNOWN'
            name = 'UNKNOWN'
            neighborhoods= 'UNKNOWN'
            full_address= 'UNKNOWN'
            city= 'UNKNOWN'
            state= 'UNKNOWN'
            latitude= 'UNKNOWN'
            longitude= 'UNKNOWN'
            stars= 2.5
            review_count= 0
            photo_url= 'UNKNOWN'
            categories= 'UNKNOWN'
            open= 'UNKNOWN'
            schools= 'UNKNOWN'
            url= restaurantMainPage

            seenDict = {}
            notrecommendedR = []
            recommendedR = []

            for tag in attributeTags:
                type= extractTagAttribute(tag, type, verbose, attrs={'property':'og:type'})
                business_id = extractTagAttribute(tag, business_id, verbose, attrs={'name':'yelp-biz-id'})
                name = extractTagAttribute(tag, name, verbose, attrs={'property':'og:title'})
                neighborhoods= 'UNKNOWN'
                full_address= 'UNKNOWN'
                city= 'UNKNOWN'
                state= 'UNKNOWN'
                latitude= 'UNKNOWN'
                longitude= 'UNKNOWN'
                stars= float(extractTagAttribute(tag, stars, verbose, attrs={'itemprop':'ratingValue'}))
                review_count= int(extractText(tag, review_count, verbose, attrs={'itemprop':'reviewCount'}))
                photo_url= 'UNKNOWN'
                categories= 'UNKNOWN'
                open= 'UNKNOWN'
                schools= 'UNKNOWN'
                url= url

                recommendedR.extend(getReviews(seenDict, tag, verbose))

            for nrtag in nrTags:
                notrecommendedR.extend(getReviews(seenDict, nrtag, verbose))

            #print 'B  : ', [type,business_id,name,neighborhoods, full_address,city,state,latitude,longitude,stars,review_count,photo_url,categories,open,schools,url]
            print 'B=', [business_id,name,stars,review_count, url]
            print 'R=', recommendedR
            print 'NR=', notrecommendedR
            #print '-'*100
    return True


def crawl(zipcode=None):
    flag = True
    some_zipcodes = [zipcode] if zipcode else get_zips()
    if zipcode is None:
        print '\n**Attempting to extract all zipcodes in the U.S'
        
    for zipcode in some_zipcodes:
        #print '\n===== Attempting extraction for zipcode <', zipcode, '>=====\n'
        try:
            while flag:
                flag = crawl_page(zipcode)
                if not flag:
                    print 'Extraction stopped or broke at zipcode'
                else:
                    break
                time.sleep(random.randint(1, 2) * .931467298)
        except Exception, e:
                print zipcode, e
                time.sleep(random.randint(1, 4) * .931467298)


if __name__ == '__main__':
    #parser = argparse.ArgumentParser(description='Extracts all yelp restaurant \
      #  data from a specified zip code (or all American zip codes if nothing \
       # is provided)')
    #parser.add_argument('-z', '--zipcode', type=int, help='Enter a zip code \
     #   you\'t like to extract from.')
    #args = parser.parse_args()
    crawl()
