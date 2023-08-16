import constants
from gensim.models import KeyedVectors
#import gensim.downloader as api

#model = api.load(model_name)
#word2vec_file = "word2vec-google-news-300.model"
model = KeyedVectors.load(constants.WORD2VEC_FILE)

import re
from rapidfuzz.process import extract
from rapidfuzz.distance import Levenshtein

# Distractor Generation Helpers
def clean_answer(answer: str) -> str:
    stage_0 = answer.split(' ')
    stage_1 = [word for word in stage_0 if word.lower() not in constants.STOPWORDS]
    stage_2 = [val[0].isupper() for val in stage_1]
    if any(stage_2):
        stage_3 = answer.title()
    else:
        stage_3 = answer.lower()
    stage_4 = re.sub(' ', '_', stage_3)
    return stage_4


def clean_distractors(distractors: list[str], cleaned_answer: str) -> list[str]:
    distractors = [re.sub('_|-',' ',value[0]) for value in distractors]
    # filter redundant distractors
    cleaned_distractors = [re.sub('\s+', ' ', value) for value in distractors]
    # remove distractors which contain answer (exact match)
    cleaned_distractors = [value for value in cleaned_distractors 
                           if value.lower() not in cleaned_answer.lower()]
    return cleaned_distractors


def filter_distractors(cleaned_distractors: list[str], cleaned_answer: str) -> list[str]:
    filtered_distractors = extract(query=cleaned_answer, choices=cleaned_distractors,
                                   scorer=Levenshtein.distance, limit=None)
    filtered_distractors = list(filter(lambda y: y[1]>3, filtered_distractors))
    filtered_distractors.sort(key=lambda x: x[2])
    filtered_distractors = list(map(lambda x:x[0], filtered_distractors))
    return filtered_distractors


def generate_disctractors(answer: str, distractor_limit: int=10) -> list[str]:
    try:
        cleaned_answer = clean_answer(answer)
        distractors = model.most_similar(cleaned_answer, topn=20)
        cleaned_distractors = clean_distractors(distractors, cleaned_answer)
        filtered_distractors = filter_distractors(cleaned_distractors, cleaned_answer)[:distractor_limit]
        print(f'Generated distractor for {answer}')
        return filtered_distractors

    except KeyError:
        print(f'No matching word found for {answer} in Word2Vec')
        return ['' for _ in range(distractor_limit)]
