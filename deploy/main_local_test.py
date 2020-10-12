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
             
bow_words = ['100', 'abl', 'absolut', 'actual', 'adjust', 'afford', 'air', 'alreadi', 'amaz', 'amazon', 'ani', 'apart', 'area', 'arm', 'armrest', 'arriv', 'assembl', 'attach', 'awesom', 'base', 'beat', 'beauti', 'becaus', 'bed', 'bedroom', 'befor', 'bench', 'better', 'big', 'bigger', 'bit', 'black', 'board', 'bolt', 'bought', 'box', 'breath', 'bubbl', 'bug', 'bui', 'build', 'built', 'came', 'cat', 'chair', 'cheap', 'chose', 'clear', 'coffe', 'color', 'come', 'comfort', 'compani', 'complet', 'comput', 'condit', 'confus', 'corner', 'couch', 'couldn', 'coupl', 'cover', 'cushion', 'dai', 'damag', 'daughter', 'deep', 'definit', 'deliv', 'deliveri', 'design', 'desk', 'desktop', 'didnt', 'dimens', 'direct', 'disappoint', 'doe', 'doesnt', 'dog', 'dollar', 'dont', 'door', 'drawer', 'drill', 'dure', 'eas', 'easi', 'easier', 'easili', 'email', 'end', 'especi', 'everi', 'everyon', 'everyth', 'exactli', 'excess', 'expect', 'extra', 'extrem', 'fabric', 'fall', 'fast', 'feel', 'fine', 'firm', 'fit', 'fix', 'follow', 'frame', 'friend', 'fulli', 'function', 'furnitur', 'game', 'gap', 'gave', 'god', 'goe', 'good', 'got', 'great', 'guess', 'gui', 'ha', 'handi', 'happi', 'hard', 'hassl', 'headboard', 'help', 'higher', 'highli', 'hold', 'hole', 'home', 'hour', 'howev', 'husband', 'ikea', 'instal', 'instruct', 'issu', 'job', 'kid', 'kitchen', 'know', 'larg', 'late', 'lb', 'left', 'leg', 'let', 'limit', 'line', 'liter', 'littl', 'long', 'look', 'lot', 'love', 'low', 'lower', 'lumbar', 'mai', 'major', 'match', 'materi', 'mattress', 'mechan', 'mid', 'min', 'mind', 'minut', 'monei', 'monitor', 'month', 'neatli', 'need', 'nice', 'offic', 'onc', 'onli', 'open', 'order', 'otherwis', 'overal', 'pack', 'packag', 'pai', 'part', 'peopl', 'perfect', 'perfectli', 'person', 'pictur', 'piec', 'place', 'plai', 'plastic', 'pleas', 'pot', 'power', 'pre', 'pretti', 'price', 'pro', 'probabl', 'problem', 'product', 'properli', 'protect', 'provid', 'purchas', 'push', 'qualiti', 'quick', 'rais', 'rate', 'read', 'real', 'reclin', 'recommend', 'rel', 'remot', 'replac', 'report', 'respons', 'rest', 'return', 'review', 'right', 'room', 'sai', 'said', 'satisfi', 'scratch', 'screw', 'seat', 'second', 'send', 'set', 'ship', 'short', 'simpl', 'sinc', 'sit', 'size', 'sleep', 'small', 'smaller', 'smell', 'snap', 'sofa', 'soft', 'solid', 'someon', 'someth', 'son', 'sort', 'space', 'spot', 'stai', 'stand', 'start', 'steal', 'stick', 'straight', 'strong', 'stuff', 'sturdi', 'super', 'support', 'suppos', 'sure', 'tabl', 'tall', 'tell', 'terribl', 'thank', 'thing', 'think', 'thought', 'tighten', 'time', 'togeth', 'took', 'tool', 'total', 'try', 'underneath', 'understand', 'updat', 'valu', 'video', 'wai', 'wall', 'want', 'wasnt', 'wast', 'weigh', 'weight', 'went', 'wheel', 'wife', 'wobbl', 'won', 'wood', 'work', 'worth', 'wrap', 'year']
      
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


# Load in the review data
import sys

reviews = ["Really comfortable, love the style , however it’s not leather , so if you sit on chair for a while the fabric will begin to move. It is over priced I think but I really loved the chair so for me it was worth it .",
"Good chair. Very easy to assemble...very adjustable. Faux gives it a great leather appearance",
"It’s only been one week, but that’s 50 hours of zoom meetings without any issues. I wish it went about an inch lower because my feet aren’t quite flat, but it’s comfortable and feels sturdy. I also wish the arms were adjustable, but the high back is a life-saver. Easy to assemble, but I made a few mistakes due to very poor written instructions. But overall, I think I’m going to be happy with this chair for quite a while."]
logreg = joblib.load('../models/BoW_logistic_regression.pkl')
lda_cv = joblib.load('../models/lda_cv.pkl')
lda = joblib.load('../models/lda_model.pkl')

# A list to store all of our (unprocessed) sentences
sentences = []
# A list of all processed sentences
clean_sentences = []
# Store each sentence vector
bow_vectors = []
# Store each sentence topic probability
sentence_probabilities = []

# Clean the text of each sentence
for review in reviews:
    for sentence in gensim.summarization.textcleaner.get_sentences(review):
        print(sentence)
        sentences.append(sentence)
        # Clean the text
        clean_sentence = preprocess_sentence(sentence, my_filter)
        clean_sentences.append(clean_sentence)
        # Compute the sentence vector
        sentence_vector = []
        for token in bow_words:
            if token in clean_sentence:
                sentence_vector.append(1)
            else:
                sentence_vector.append(0)
        # Append the sentence vector to our collection
        bow_vectors.append(sentence_vector)
        # Compute the topic probability of the words in our sentence
        word_probabilities = lda.transform(lda_cv.transform(clean_sentence))
        # Compute topic probability of the sentence
        sentence_probability = [*map(np.mean, zip(*word_probabilities))]
        # Store in list
        sentence_probabilities.append(sentence_probability)
        
    
print(bow_vectors[0])
# Put into the model to see what sentences are about assembly
predictions = logreg.predict(bow_vectors)

# Assign sentiment to the predicted assembly sentences
ratings = 0
number_ratings = 0
tool = 0.
tool_total = 0.
time = 0.
time_total = 0.
quality = 0.
quality_total = 0.
for i in range(0, len(sentences)):
    if predictions[i] == 1:
        now_sentiment = get_sentiment(sentences[i])
        ratings += get_sentiment(sentences[i])
        number_ratings += 1.
        # Weight the sentiment by the subtopic rating
        tool += (now_sentiment * sentence_probabilities[i][0])
        tool_total += sentence_probabilities[i][0]
        time += (now_sentiment * sentence_probabilities[i][1])
        time_total += sentence_probabilities[i][1]
        quality += (now_sentiment * sentence_probabilities[i][2])
        quality_total += sentence_probabilities[i][2]
      
tool /= tool_total
time /= time_total
quality /= quality_total
tool = round(tool, 1)
time = round(time, 1)
quality = round(quality, 1)

# Take the average
try:
    cumulative_rating = ratings / number_ratings
except:
    cumulative_rating = 3.0
    
# We want to give the user one decimal place
output = round(cumulative_rating, 1)
# Return 3 reviews that mention assembly
ones = [index for index, element in enumerate(predictions) if element == 1]
random_sentence = random.sample(range(0, len(ones)), 2)
    
print(str(output), str(tool), str(time), str(quality),sentences[ones[random_sentence[0]]], sentences[ones[random_sentence[1]]])

