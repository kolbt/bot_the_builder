'''
Writing the python file that my javascript will call (from Amazon Lambda)
'''
# Run with
# serverless invoke local -f assembly-rating -d '{"body":[["Very difficult to assemble!"], ["Parts did not fit together well at all."], ["Very hard to put together, it took me over an hour!"]]}'
import gensim
import pickle
from sklearn.linear_model import LogisticRegression
import json
import numpy as np
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import joblib
import boto3
from nltk.tokenize import word_tokenize
#import wget

def get_model():
    '''Download our models from the aws buckets'''
    bucket = boto3.resource('s3').Bucket('insight-deploy-kolb')
    embedding = bucket.download_file('pre_trained_w2v.model', '/tmp/embedding.model')
    logreg = bucket.download_file('pre_trained_w2v_logistic_regression.pkl', '/tmp/logreg.pkl')
    embedding_model = gensim.models.Word2Vec.load('/tmp/embedding.model')
    embedding_model.init_sims(replace=True)
    logreg_fit = joblib.load('/tmp/logreg.pkl')
#    embedding_model = gensim.models.Word2Vec.load(embedding)
#    logreg_fit = joblib.load(logreg)
    return embedding_model, logreg_fit

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

def lambda_handler(event, context):

    # Load in the text data
    sentences = event['body']
    
    # Load our models
    embedding, logreg = get_model()
    
    # Compute the mean for each sentence
    means = []
    for sentence in sentences:
        tokenized = word_tokenize(sentence[0])
        means.append(word_averaging(embedding.wv, tokenized))
        
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
