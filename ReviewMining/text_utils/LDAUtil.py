__author__ = 'santhosh'

import gensim
import nltk
import stop_words

import TextConstants


nltk.data.path.append(TextConstants.NLTK_DATA_PATH)
en_stop = stop_words.get_stop_words('en')
tokenizer = nltk.tokenize.RegexpTokenizer(r'\w+')
p_stemmer = nltk.stem.porter.PorterStemmer()

def tokenizeReviewText(review_text):
    raw = review_text.lower()
    review_text_tokens = tokenizer.tokenize(raw)
    return review_text_tokens

def removeStopWordsForReview(review_text_tokens):
    stopped_tokens = [i for i in review_text_tokens if not i in en_stop]
    return stopped_tokens

def performStemmingforReview(review_text_stopped_tokens):
    stemmed_tokens = [p_stemmer.stem(i) for i in review_text_stopped_tokens]
    return stemmed_tokens

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
        tokens = removeStopWordsForReview(tokens)
        tokens = performStemmingforReview(tokens)
        texts.append(tokens)
    corpus, dictionary = createDocumentWordMatrix(texts)
    return performLDA(corpus, dictionary, num_topics=num_topics, num_words=num_words)