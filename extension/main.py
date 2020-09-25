'''
Writing the python file that my javascript will call (from Amazon Lambda)
'''
from flask import escape
import gensim
import pickle
from sklearn.linear_model import LogisticRegression
import requests
import json
import numpy as np
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import joblib
import wget
    
bucket_name = 'insightdatascience7970-aiplatform'
blob_name_embedding = 'pre_trained_w2v.model'
blob_name_logreg = 'pre_trained_w2v_logistic_regression.pkl'

# Load the relevant models
#w2v_file = "../notebooks/pre_trained_w2v.model"
#logreg_file = "../notebooks/pre_trained_w2v_logistic_regression.pkl"

w2v_file = '/tmp/' + blob_name_embedding
logreg_file = '/tmp/' + blob_name_logreg

embedding_file = wget.download('https://storage.googleapis.com/insightdatascience7970-aiplatform/pre_trained_w2v.model', w2v_file)
logreg_file = wget.download('https://storage.googleapis.com/insightdatascience7970-aiplatform/pre_trained_w2v_logistic_regression.pkl', logreg_file)

embedding = gensim.models.Word2Vec.load(w2v_file)
logreg = joblib.load(logreg_file)

# The simplest way to get a value for the sentence is to take the mean
def word_averaging(wv, sentence):
    '''Get the average normalized word vector for a sentence'''
    all_words, mean = set(), []
    for word in sentence:
        if isinstance(word, np.ndarray):
            mean.append(word)
        elif word in wv.vocab:
            mean.append(wv.vectors_norm[wv.vocab[word].index])
            all_words.add(wv.vocab[word].index)
    if not mean:
        return np.zeros(wv.vector_size,)

    mean = gensim.matutils.unitvec(np.array(mean).mean(axis=0)).astype(np.float32)
    return mean
    
def get_sentiment(sentence):
    '''Assign sentiment to any give sentence using VADER'''
    # Instantiate the sentiment analyzer
    sentiment = SentimentIntensityAnalyzer()
    # Get the sentiment dictionary for my sentence
    sentiment_dict = sentiment.polarity_scores(sentence)
    # Output the compound sentiment (between [-1, 1])
    out = sentiment_dict['compound']
    # Renormalize this to be [1, 5]
    stars = (out * 2.) + 3.
    return stars

def read_article(file_json):
    '''Convert json file to sentences'''
    article = ''
    filedata = json.dumps(file_json)
    if len(filedata) < 100000:
        article = filedata
    return article

# Load the text data sent from JavaScript
def provide_rating(request):
    
    # Load in the text data
    request_json = request.get_json(silent=True)
    sentences = read_article(request_json)
    
    # Compute the mean for each sentence
    means = []
    for sentence in sentences:
        means.append(word_averaging(embedding, sentence))
        
    # Put into the model to see what sentences are about assembly
    predictions = logreg.predict(means)
    
    # Assign sentiment to the predicted assembly sentences
    ratings = 0
    number_ratings = 0
    for i in range(0, len(sentences)):
        if predictions[i] == 1:
            ratings += get_sentiment(sentences[i])
            number_ratings += 1.
            
    # Take the average
    cumulative_rating = ratings / number_ratings
    return json.dumps(cumulative_rating)
