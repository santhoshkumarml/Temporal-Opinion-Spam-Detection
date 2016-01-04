'''
@author: santhosh
'''
import gensim
import nltk
import stop_words

import TextConstants


nltk.data.path.append(TextConstants.NLTK_DATA_PATH)
en_stop = stop_words.get_stop_words('en')
tokenizer = nltk.tokenize.RegexpTokenizer(r'\w+')
p_stemmer = nltk.stem.porter.PorterStemmer()

def tokenizeReviewText(review_text):
    return tokenizer.tokenize(review_text.lower())

def removeStopWordsForReview(review_text_tokens):
    return [token for token in review_text_tokens if not token in en_stop]

def performStemmingforReview(review_text_stopped_tokens):
    return [p_stemmer.stem(token) for token in review_text_stopped_tokens]

def createDocumentWordMatrix(texts):
    dictionary = gensim.corpora.Dictionary(texts)
    corpus = [dictionary.doc2bow(text) for text in texts]
    return corpus, dictionary

def performLDA(corpus, dictionary,num_topics=3, num_words=1):
    ldamodel = gensim.models.ldamodel.LdaModel(corpus,
                                               num_topics=num_topics,
                                               id2word = dictionary,
                                               passes=20)
    return ldamodel.print_topics(num_topics=num_topics, num_words=num_words)

def performLDAOnReviews(reviews, num_topics=3, num_words=1):
    review_texts = [revw.getReviewText() for revw in reviews]
    texts = []
    for review_text in review_texts:
        tokens = tokenizeReviewText(review_text)
        stopped_tokens = removeStopWordsForReview(tokens)
        stemmed_tokens = performStemmingforReview(stopped_tokens)
        texts.append(stemmed_tokens)
    if len(texts) == 0:
        print 'No Reviews with review texts'
    try:
        corpus, dictionary = createDocumentWordMatrix(texts)
        return performLDA(corpus, dictionary, num_topics=num_topics, num_words=num_words)
    except ValueError as e:
        return 'No Data to LDA'