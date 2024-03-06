import re
import spacy
import constants
import pandas as pd
from torch import topk
from sentence_transformers import SentenceTransformer, util
from __future__ import annotations

def concat_distractors(row):
    '''
    Concatenate all distractors from Word2Vec and T5.
    '''
    combined_distrs = [row['distractor_0'], row['distractor_1'], row['distractor_2'], row['distractor_3'],
                       row['distractor_4'], row['distractor_5'], row['distractor_6'], row['distractor_7'],
                       row['distractor_8'], row['distractor_9']]
    combined_distrs.extend(row['cleaned_w2v_distr'])
    return combined_distrs


def lemmatize(distr_list):
    '''
    Lemmatize all words. This prevents same words in different forms from being
    shown as possible distractors.
    '''
    docs = [nlp(word) for word in distr_list]
    # Dict with lemmatized word as key and original word as value.
    # This ensures only unique lemmatized words are preserved (no duplicate keys)
    lemma_dist_dict = {}
    for doc in docs:
        lemmas = [token.lemma_ for token in doc]
        joined_lemmas = ' '.join(lemmas)
        lemma_dist_dict[joined_lemmas] = doc.text
    lemmatized_distr = list(lemma_dist_dict.values())
    return lemmatized_distr


def compute_cosim(row):
    '''
    Computes cosine similarity.
    Returns list of top-n-best-matching distractors, sorted in decreasing similarity.
    '''
    distr_emb = model.encode(row['combined_distractors'], convert_to_tensor=True, device='cuda')
    score = util.cos_sim(row['query_emb'], distr_emb.cpu())
    top_results = topk(score, k=constants.TOP_N_DISTR)
    top_indices = top_results.indices[0].tolist()
    top_distrs = [row['combined_distractors'][index] for index in top_indices]
    return top_distrs


def find_best_match_distr(df):
    '''
    Compute cosine similarity between combined distractors' list and query for every row.
    '''
    query_emb = model.encode(df['query'].values, convert_to_tensor=True, device='cuda')
    df['query_emb'] = query_emb.cpu().tolist()
    df['best_matching_distr'] = df.apply(lambda row: compute_cosim(row), axis=1)
    df = df[['generated_question', 'generated_answer',
             'cleaned_T5_distr', 'best_matching_distr']]
    return df


def split_distractors(distractors: list[str]) -> list[str]:
    '''
    Split distractors based on "and", "or", etc.
    '''
    merged_distr = []
    for value in distractors:
        split_value = re.split(r'\s+(and|or)\s+', value)
        non_empty = [val.strip() for val in split_value if val not in (' ', '', 'and', 'or')]
        merged_distr.append(non_empty)

    flattened_distr = [leaf for tree in merged_distr for leaf in tree]
    return flattened_distr


def remove_identicals(row):
    #lowered_distr = [val.lower() for val in row['cleaned_T5_distr']]
    #unique_distr = list(filter(lambda x: x!= row['generated_answer'].lower(), lowered_distr))
    unique_distr = list(filter(lambda x: x!=row['generated_answer'], row['cleaned_T5_distr']))
    return unique_distr


def prepare_data(df):
    '''
    Prepares CSV containing question, answer, T5 and Word2Vec distractors.
    '''
    df['query'] = df['generated_question']+' '+df['generated_answer']+'.'
    df['cleaned_w2v_distr'] = (df['cleaned_distr']
                               .apply(lambda x: x.strip(r'[|]'))
                               .apply(lambda x: re.sub("'", "", x))
                               .apply(lambda x: x.split(',')))
    df['combined_distractors'] = df.apply(lambda row: concat_distractors(row), axis=1)
    df['combined_distractors'] = df['combined_distractors'].apply(lambda x: lemmatize(x))
    df['cleaned_T5_distr'] = df['T5_distractors'].apply(lambda x: x.split(','))
    df['cleaned_T5_distr'] = df['cleaned_T5_distr'].apply(lambda x: split_distractors(x))
    df['cleaned_T5_distr'] = df.apply(lambda row: remove_identicals(row), axis=1)
    return df


nlp = spacy.load('en_core_web_sm')
model = SentenceTransformer(constants.EMBEDDING_MODEL)

df = pd.read_csv('T5_distractors.csv')
df = prepare_data(df)
df = find_best_match_distr(df)
df.to_csv('T5_best_match_distr.csv', index=False)
