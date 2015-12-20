__author__ = 'santhosh'

import nltk
import TextConstants
import stop_words
import gensim

nltk.data.path.append(TextConstants.NLTK_DATA_PATH)
en_stop = stop_words.get_stop_words('en')

def tokenizeReviewText(review_text):
    tokenizer = nltk.tokenize.RegexpTokenizer(r'\w+')
    raw = review_text.lower()
    review_text_tokens = tokenizer.tokenize(raw)
    return review_text_tokens

def removeStopWordsForReview(review_text_tokens):
    stopped_tokens = [i for i in review_text_tokens if not i in en_stop]
    return stopped_tokens

def performStemmingforReview(review_text_stopped_tokens):
    p_stemmer = nltk.stem.porter.PorterStemmer()
    stemmed_tokens = [p_stemmer.stem(i) for i in review_text_stopped_tokens]
    return stemmed_tokens

def createDocumentWordMatrix(texts):
    dictionary = gensim.corpora.Dictionary(texts)
    corpus = [dictionary.doc2bow(text) for text in texts]
    return corpus, dictionary

def performLDA(corpus, dictionary):
    ldamodel = gensim.models.ldamodel.LdaModel(corpus,
                                               num_topics=3,
                                               id2word = dictionary,
                                               passes=20)
    print(ldamodel.print_topics(num_topics=3, num_words=3))