from __future__ import annotations
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import pandas as pd
import constants
import re

def generate_prompts(df:pd.DataFrame) -> list(str):
    prompts = []
    for row in df.itertuples():
        prompt=f'''Generate three possible incorrect answers for the question and answer given below.
                Question: {row.generated_question}
                Answer: {row.generated_answer}
                Choices:
                '''
        prompts.append(prompt)
    return prompts


def generate_T5_distractors(df):
    generated_distractors = []
    #chunk_size = 20
    prompts = generate_prompts(df)

    for chunk in range(0, len(prompts), constants.CHUNK_SIZE):
        print(f'\n{chunk}:{chunk+constants.CHUNK_SIZE}')
        chunked_prompts = prompts[chunk:chunk+constants.CHUNK_SIZE]
        input_ids = tokenizer(chunked_prompts,
                            return_tensors="pt",
                            max_length=130,
                            truncation=True,
                            padding=True).input_ids.to('cuda')
        outputs = model.generate(input_ids,
                                num_beams=1,
                                max_length=20,
                                num_beam_groups=1,
                                num_return_sequences=1,
                                no_repeat_ngram_size=2,
                                early_stopping=True,
                                repetition_penalty=1.2,
                                length_penalty=1.2)
                                #output_scores=True)
                                #diversity_penalty=0.75)
        result = tokenizer.batch_decode(outputs, skip_special_tokens=True)
        generated_distractors.append(result)

    distactors_list = [distractor for chunks in generated_distractors for distractor in chunks]
    df.loc[:, 'T5_distractors'] = distactors_list
    return df


def split_distractors(distractors: list[str]) -> list[str]:
    merged_distr = []
    for value in distractors:
        split_value = re.split(r'\s+(and|or)\s+', value)
        non_empty = [val.strip() for val in split_value if val not in (' ', '', 'and', 'or')]
        merged_distr.append(non_empty)

    flattened_distr = [leaf for tree in merged_distr for leaf in tree]
    return flattened_distr


def remove_identicals(row):
    lowered_distr = [val.lower() for val in row['cleaned_distr']]
    unique_distr = list(filter(lambda x: x!= row['generated_answer'].lower(), lowered_distr))
    return unique_distr


def clean_distractors(df):
    df['cleaned_distr'] = df['T5_distractors'].apply(lambda x: x.split(','))
    df['cleaned_distr'] = (df['cleaned_distr']
                           .apply(lambda x: x if len(x)>=2 else [''])
                           .apply(lambda x: split_distractors(x)))
    df['cleaned_distr'] = df.apply(lambda row: remove_identicals(row), axis=1)
    return df


tokenizer = AutoTokenizer.from_pretrained("google/flan-t5-xl", cache_dir="D:\huggingface",
                                          device_map='auto', model_max_length=130,
                                          device='cuda', force_download=False)
model = AutoModelForSeq2SeqLM.from_pretrained("google/flan-t5-xl", cache_dir="D:\huggingface",
                                              min_length=3, device_map='auto',
                                              force_download=False, offload_folder='offload')

df = pd.read_csv('unique_filtered_QA_distractors.csv')
# TODO: remove flag, later have to do it for all rows.
df = df[df['flag']==0]
df = generate_T5_distractors(df)
df = clean_distractors(df)
df.to_csv('T5_distractors.csv', index=False)

# For back-question-answered data
df = pd.read_csv('final_back_questioned_QA.csv')
# TODO: remove flag, later have to do it for all rows.
#df = df[df['flag']==0]
df = df[['generated_question0', 'generated_answer0']]
df.columns = ['generated_question', 'generated_answer']
df = generate_T5_distractors(df)
df = clean_distractors(df)
df.to_csv('T5_distractors_back_questioned.csv', index=False)
