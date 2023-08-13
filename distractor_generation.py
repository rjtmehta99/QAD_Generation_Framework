import re
from nltk import edit_distance
import gensim.downloader as api
from gensim.models import Word2Vec
from gensim.models import KeyedVectors
from rapidfuzz.process import extract
from rapidfuzz.distance import Levenshtein

model_name = "word2vec-google-news-300"
model = api.load(model_name)
model = KeyedVectors.load('data/word2vec-google-news-300.model')
#model.save('data/word2vec-google-news-300.model')
#model = Word2Vec.load('data/word2vec-google-news-300.model')
#model = KeyedVectors.load_word2vec_format('data/word2vec-google-news-300.model')

answer = 'co2'
try:
    stage_0 = answer.split(' ')
    stage_1 = [val[0].isupper() for val in stage_0]
    if any(stage_1):
        stage_2 = answer.title()
    else:
        stage_2 = answer.lower()
    
    stage_3 = re.sub(' ', '_', stage_2)
    distractors = model.most_similar(stage_3, topn=20)
    distractors = [re.sub('_',' ',value[0]) for value in distractors]
    # filter redundant distractors
    #distractors = extract('name', ['names', 'naam', 'boom'], scorer=Levenshtein.distance)
    #v = list(z)
    #v
    z = filter(lambda y: y[1]>2, x)

    filtered_distractors = []
    for x in distractors:
        print(x)

except KeyError:
    print('No matching word found in Word2Vec')

