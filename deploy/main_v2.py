'''
This file will be hosted on AWS Lambda and called by the endpoint in the chrome extension
1.) Loads the required logistic regression
2.) Preprocess the review text
3.) Compute the word vetor of each sentence (count vectorized)
4.) Predict which sentences are about assembly
5.) Compute sentiment of these sentences
6.) Grab three random review sentences
7.) Returns ease of assembly and a few sentences to user
'''

import gensim
import gensim.parsing.preprocessing as gpp
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import CountVectorizer
import json
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import joblib
import boto3
import random

# This are the words determined by BoW
bow_words = ['100', 'abl', 'abl assembl', 'abl togeth', 'absolut', 'actual', 'adjust',
             'afford', 'air', 'alreadi', 'amaz', 'amazon', 'ani', 'ani issu', 'apart',
             'ar', 'ar easi', 'ar realli', 'area', 'area ar', 'arm', 'arm rest', 'armrest',
             'arriv', 'assembl', 'assembl chair', 'assembl easi', 'assembl fit',
             'assembl sturdi', 'assembl took', 'assembl wa', 'attach', 'attach seat',
             'awesom', 'base', 'beat', 'beauti', 'becaus', 'bed', 'bed frame',
             'bed mattress', 'bedroom', 'befor', 'bench', 'better', 'better expect', 'big',
             'bigger', 'bigger thi', 'bit', 'black', 'board', 'bolt', 'bought', 'bought thi',
             'box', 'breath', 'bubbl', 'bubbl wrap', 'bug', 'bui', 'bui thi', 'build', 'built',
             'came', 'came wrap', 'cat', 'chair', 'chair bench', 'chair easi', 'chair small',
             'chair took', 'chair wa', 'chair work', 'cheap', 'chose', 'clear', 'coffe',
             'coffe tabl', 'color', 'color wa', 'come', 'comfort', 'comfort chair',
             'comfort sit', 'compani', 'complet', 'comput', 'comput monitor', 'condit',
             'confus', 'corner', 'couch', 'couldn', 'coupl', 'cover', 'cushion', 'dai', 'damag',
             'daughter', 'deep', 'definit', 'deliv', 'deliveri', 'design', 'desk', 'desktop',
             'didnt', 'dimens', 'direct', 'direct clear', 'disappoint', 'disappoint thi', 'doe',
             'doesnt', 'doesnt fit', 'dog', 'dollar', 'dont', 'door', 'drawer', 'drill',
             'drill hole', 'dure', 'eas', 'easi', 'easi assembl', 'easi build', 'easi follow',
             'easi instal', 'easi togeth', 'easi understand', 'easier', 'easili', 'email',
             'end', 'end tabl', 'especi', 'everi', 'everyon', 'everyth', 'everyth wa',
             'exactli', 'excess', 'expect', 'extra', 'extrem', 'fabric', 'fall', 'fast',
             'feel', 'feel like', 'fine', 'firm', 'fit', 'fit perfect', 'fit perfectli',
             'fix', 'follow', 'frame', 'friend', 'fulli', 'function', 'furnitur', 'game',
             'gap', 'gave', 'god', 'goe', 'good', 'good look', 'good valu', 'got', 'got thi',
             'great', 'great chair', 'great price', 'great product', 'great qualiti', 'great tabl',
             'great veri', 'guess', 'gui', 'ha', 'handi', 'happi', 'happi purchas', 'hard',
             'hard togeth', 'hassl', 'headboard', 'help', 'higher', 'highli', 'highli recommend',
             'hold', 'hole', 'home', 'hour', 'howev', 'husband', 'ikea', 'ikea stuff', 'instal',
             'instruct', 'issu', 'job', 'kid', 'kitchen', 'know', 'larg', 'late', 'lb', 'left', 'leg',
             'let', 'like', 'like fall', 'limit', 'line', 'liter', 'littl', 'long', 'look', 'look great',
             'look nice', 'lot', 'love', 'love thi', 'low', 'lower', 'lumbar', 'lumbar support', 'mai',
             'major', 'match', 'match coffe', 'materi', 'materi ar', 'mattress', 'mechan', 'mid',
             'min', 'mind', 'minut', 'minut assembl', 'monei', 'monitor', 'month', 'neatli', 'need',
             'nice', 'offic', 'onc', 'onli', 'onli ha', 'open', 'order', 'order thi', 'otherwis',
             'overal', 'overal extrem', 'overal thi', 'pack', 'packag', 'pai', 'peopl', 'perfect',
             'perfect apart', 'perfect condit', 'perfectli', 'person', 'pictur', 'piec', 'place',
             'plai', 'plastic', 'pleas', 'pot', 'power', 'pre', 'pre drill', 'pretti', 'price',
             'price veri', 'pro', 'probabl', 'probabl took', 'problem', 'product', 'properli',
             'protect', 'provid', 'purchas', 'push', 'qualiti', 'quick', 'rais', 'rate', 'read',
             'real', 'realli', 'reclin', 'recommend', 'recommend thi', 'rel', 'rel easi', 'remot',
             'replac', 'report', 'respons', 'rest', 'return', 'review', 'right', 'right desk', 'room',
             'sai', 'said', 'satisfi', 'scratch', 'screw', 'screw ar', 'screw leg', 'screw screw',
             'seat', 'seat cushion', 'second', 'send', 'set', 'ship', 'short', 'simpl', 'simpl assembl',
             'sinc', 'sit', 'size', 'size perfect', 'sleep', 'small', 'small space', 'smaller', 'smell',
             'snap', 'sofa', 'soft', 'solid', 'someon', 'someth', 'son', 'sort', 'space', 'spot', 'stai',
             'stand', 'start', 'steal', 'stick', 'straight', 'strong', 'stuff', 'stuff thi', 'sturdi',
             'sturdi easi', 'sturdi veri', 'super', 'super comfort', 'super easi', 'support', 'support area',
             'suppos', 'sure', 'tabl', 'tabl great', 'tabl look', 'tall', 'tell', 'terribl', 'thank',
             'thank great', 'thei', 'thei ar', 'thi', 'thi chair', 'thi compani', 'thi couch', 'thi desk',
             'thi good', 'thi great', 'thi product', 'thi tabl', 'thi togeth', 'thi wa', 'thing', 'think',
             'thought', 'tighten', 'time', 'togeth', 'togeth hour', 'togeth minut', 'togeth wa', 'took',
             'took min', 'took minut', 'took time', 'tool', 'total', 'try', 'underneath', 'understand',
             'updat', 'valu', 'veri', 'veri comfort', 'veri disappoint', 'veri easi', 'veri firm', 'veri littl',
             'veri pleas', 'veri satisfi', 'veri simpl', 'veri sturdi', 'veri veri', 'video', 'wa', 'wa abl',
             'wa assembl', 'wa better', 'wa deliv', 'wa easi', 'wa littl', 'wa look', 'wa nice', 'wa super',
             'wa veri', 'wai', 'wai chair', 'wall', 'want', 'want someth', 'wasnt', 'wasnt hard', 'wast',
             'wast monei', 'weigh', 'weight', 'went', 'went togeth', 'wheel', 'wife', 'wobbl', 'won', 'wood',
             'work', 'work bench', 'work dai', 'work home', 'work space', 'worth', 'worth monei', 'wrap',
             'wrap bubbl', 'year']
      
# The preprocessing filters
my_filter = [lambda x: x.lower(),
                    gpp.strip_tags,
                    gpp.split_alphanum,
                    gpp.strip_non_alphanum,
                    gpp.strip_punctuation,
                    gpp.strip_multiple_whitespaces,
                    gpp.stem_text,
                    gpp.strip_short]
                    
# Get a custom list of stopwords
stops = list(gpp.STOPWORDS)
stops.remove("part")

def get_model():
    '''Download our models from the aws buckets'''
    bucket = boto3.resource('s3').Bucket('builder-v1')
    
    # !!! Make sure the names match with what is in your bucket on s3 !!!
    logreg = bucket.download_file('model/BoW_logistic_regression.pkl', '/tmp/logreg.pkl')
    logreg_fit = joblib.load('/tmp/logreg.pkl')
    # Load the LDA model as well
    lda = bucket.download_file('model/lda_model.pkl', '/tmp/lda_model.pkl')
    lda_fit = joblib.load('/tmp/lda_model.pkl')
    # And the LDA vectorizer
    lda_cv = bucket.download_file('model/lda_cv.pkl', '/tmp/lda_cv.pkl')
    lda_cv_out = joblib.load('/tmp/lda_cv.pkl')
    
    return logreg_fit, lda_fit, lda_cv_out
    
def preprocess_sentence(sentence, my_filter):
    # Apply gensim filter
    out = gpp.preprocess_string(sentence, my_filter)
    # Remove custom stopwords
    for i in reversed(out):
        if i in stops:
            out.remove(i)
    # Return the tokenized words
    return out
    
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
    logreg, lda, lda_cv = get_model()
    
    # A list to store all of our (unprocessed) sentences
    sentences = []
    # A list of sentence topic probabilities
    sentence_probabilities = []
    # Store each sentence vector
    bow_vectors = []
    # Clean the text of each sentence
    for review in reviews:
        for sentence in gensim.summarization.textcleaner.get_sentences(review):
            sentences.append(sentence)
            # Clean the text
            clean_sentence = preprocess_sentence(sentence, my_filter)
            # Compute the sentence vector
            sentence_vector = []
            for token in bow_words:
                if token in clean_sentence:
                    sentence_vector.append(1)
                else:
                    sentence_vector.append(0)
            # Append the sentence vector to our collection
            bow_vectors.append(sentence_vector)
            if len(clean_sentence) < 1:
                sentence_probabilities.append([0., 0., 0.])
                continue
            # Compute the topic probability of the words in our sentence
            word_probabilities = lda.transform(lda_cv.transform(clean_sentence))
            # Compute topic probability of the sentence
            sentence_probability = [*map(np.mean, zip(*word_probabilities))]
            # Store in list
            sentence_probabilities.append(sentence_probability)
        
    # Put into the model to see what sentences are about assembly
    predictions = logreg.predict(bow_vectors)
    
    # Assign sentiment to the predicted assembly sentences
    ratings = 0.
    number_ratings = 0.
    assembly_scores = []
    tool = 0.
    tool_total = 0.
    time = 0.
    time_total = 0.
    quality = 0.
    quality_total = 0.
    for i in range(0, len(sentences)):
        if predictions[i] == 1:
            # Compute the sentiment
            sentence_sentiment = get_sentiment(sentences[i])
            ratings += sentence_sentiment
            assembly_scores.append(sentence_sentiment)
            number_ratings += 1.
#            # Weight the sentiment by the subtopic rating
#            tool += (sentence_sentiment * sentence_probabilities[i][0])
#            tool_total += sentence_probabilities[i][0]
#            time += (sentence_sentiment * sentence_probabilities[i][1])
#            time_total += sentence_probabilities[i][1]
#            quality += (sentence_sentiment * sentence_probabilities[i][2])
#            quality_total += sentence_probabilities[i][2]
            # Get the index of the highest probability topic
            category = sentence_probabilities[i].index(max(sentence_probabilities[i]))
            # Tools category
            if category == 0:
                tool += sentence_sentiment
                tool_total += 1.
            # Time category
            elif category == 1:
                time += sentence_sentiment
                time_total += 1.
            # Quality category
            else:
                quality += sentence_sentiment
                quality_total += 1.
            
        else:
            assembly_scores.append(None)
            
    # Get the max/min sentiment and the indices of the respective sentences
    sentiment_max = max(x for x in assembly_scores if x is not None)
    max_index = assembly_scores.index(sentiment_max)
    sentiment_min = min(x for x in assembly_scores if x is not None)
    min_index = assembly_scores.index(sentiment_min)
            
    # Take the average
    try:
        cumulative_rating = ratings / number_ratings
        # We want to give the user one decimal place
        output = round(cumulative_rating, 1)
    except:
        cumulative_rating = 3.0
        
    # Same for tool rating
    try:
        cumulative_tool = tool / tool_total
        out_tool = round(cumulative_tool, 1)
    except:
        out_tool = "?"
       
    # Same for time rating
    try:
        cumulative_time = time / time_total
        out_time = round(cumulative_time, 1)
    except:
        out_time = "?"
        
    # Same for quality rating
    try:
        cumulative_quality = quality / quality_total
        out_quality = round(cumulative_quality, 1)
    except:
        out_quality = "?"
    
    return [str(output), str(out_tool), str(out_time), str(out_quality), sentences[max_index], sentences[min_index]]

