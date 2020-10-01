'''
Writing the python file that my javascript will call (from Amazon Lambda)
'''

import gensim
import numpy as np
from sklearn.linear_model import LogisticRegression
import json
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import joblib
import boto3

def get_model():
    '''Download our models from the aws buckets'''
    bucket = boto3.resource('s3').Bucket('builder-v1')
    # !!! Make sure the names match with what is in your bucket on s3 !!!
    embedding = bucket.download_file('model/pre_trained_w2v.model', '/tmp/embedding.model')
    logreg = bucket.download_file('model/pre_trained_w2v_logistic_regression.pkl', '/tmp/logreg.pkl')
    embedding_model = gensim.models.Word2Vec.load('/tmp/embedding.model')
    embedding_model.init_sims(replace=True)
    logreg_fit = joblib.load('/tmp/logreg.pkl')

    return embedding_model, logreg_fit

# The simplest way to get a value for the sentence is to take the mean
def word_averaging(wv, sentence):
    '''Get the average normalized word vector for a sentence'''
    all_words, mean= set(), []
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

def lambda_handler(event, context):

    # Load in the review data
    reviews = list(event)
    
    # Load our models
    embedding, logreg = get_model()
    
    # Compute the mean for each sentence
    means = []
    sentences = []
    for review in reviews:
        for sentence in gensim.summarization.textcleaner.get_sentences(review):
            tokenized = gensim.utils.tokenize(sentence)
            means.append(word_averaging(embedding.wv, tokenized))
            sentences.append(sentence)
        
    # Put into the model to see what sentences are about assembly
    predictions = logreg.predict(means)
    out = predictions.tolist()
    
    # Assign sentiment to the predicted assembly sentences
    ratings = 0
    number_ratings = 0
    for i in range(0, len(sentences)):
        if predictions[i] == 1:
            ratings += get_sentiment(sentences[i])
            number_ratings += 1.
            
    # Take the average
    try:
        cumulative_rating = ratings / number_ratings
    except:
        cumulative_rating = 3.0
        
    return [str(cumulative_rating)]

