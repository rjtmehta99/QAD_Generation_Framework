import re
from rapidfuzz.process import extract
from rapidfuzz.distance import Levenshtein
import constants
from gensim.models import KeyedVectors
#import gensim.downloader as api
#model = api.load(model_name)
#word2vec_file = "word2vec-google-news-300.model"
model = KeyedVectors.load(constants.WORD2VEC_FILE)

def check_numeric(answer: str) -> int | None:
    """
    Check if the answer is a number written in word. If so, return the integral value. 
    Limited from 0-100.

    Args:
        answer (str): Answer string

    Returns:
        int | None: Corresponding integer or None
    """
    #stage_0 = answer.split(' ')
    #stage_1 = [constants.WORD_NUMBER_DICT[word] if word in constants.WORD_NUMBER_DICT else word for word in stage_1]
    if answer in constants.WORD_NUMBER_DICT:
        numeric_answer = constants.WORD_NUMBER_DICT[answer]
        return numeric_answer
    try:
        if int(answer):
            return int(answer)
    except ValueError:
        return None
    return None


# Distractor Generation Helpers
def clean_answer(answer: str) -> str:
    try:
        stage_0 = answer.split(' ')
    # Encountered when answer is float
    except AttributeError:
        answer = str(answer)
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


def remove_blacklisted(distractors: list[str]):
    """
    Remove blacklisted distractors from a list of distractors.
    """
    filtered_distractors = []
    for distr in distractors:
        for blisted in constants.BLACKLISTED_DISTR_WORDS:
            words = distr.split(' ')
            if blisted in words:
                break
        else:
            filtered_distractors.append(distr)
    return filtered_distractors


def filter_distractors(cleaned_distractors: list[str], cleaned_answer: str) -> list[str]:
    filtered_distractors = extract(query=cleaned_answer, choices=cleaned_distractors,
                                   scorer=Levenshtein.distance, limit=None)
    filtered_distractors = list(filter(lambda y: y[1]>3, filtered_distractors))
    filtered_distractors.sort(key=lambda x: x[2])
    filtered_distractors = list(map(lambda x:x[0], filtered_distractors))
    filtered_distractors = remove_blacklisted(filtered_distractors)
    return filtered_distractors


def generate_disctractors(answer: str, distractor_count: int=10) -> list[str]:
    try:
        numeric_answer = check_numeric(answer)
        if numeric_answer:
            #print(f'Creating numeric distractors for {answer}')
            numeric_distractors = [numeric_answer+5, numeric_answer+10, numeric_answer-5, 
                                   numeric_answer-10, numeric_answer+1, numeric_answer-1]
            # Add empty values to other distractors
            if distractor_count > len(numeric_distractors):
                remaining_count = distractor_count - len(numeric_distractors)
                remaining_values = ['' for _ in range(remaining_count)]
                numeric_distractors.extend(remaining_values)
            # Remove extra distractors
            elif distractor_count < len(numeric_distractors):
                #extra_count = len(numeric_distractors) - distractor_count
                numeric_distractors[:distractor_count]
            return numeric_distractors

        else:
            cleaned_answer = clean_answer(answer)
            distractors = model.most_similar(cleaned_answer, topn=20)
            cleaned_distractors = clean_distractors(distractors, cleaned_answer)
            filtered_distractors = filter_distractors(cleaned_distractors, cleaned_answer)[:distractor_count]
            #print(f'Generated distractor for {answer}')
            return filtered_distractors

    except KeyError:
        #print(f'No matching word found for {answer} in Word2Vec')
        return ['' for _ in range(distractor_count)]

def convert_numeric_answer(answer):
    try:
        numeric_answer = check_numeric(answer)
        if numeric_answer:
            return numeric_answer
        numeric_answer = int(answer)
        return numeric_answer
    except ValueError:
        return answer
    