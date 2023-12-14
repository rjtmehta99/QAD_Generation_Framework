import helper
from numpy import nan
import pandas as pd
from haystack.nodes import FARMReader
from haystack.utils import clean_wiki_text
from haystack.document_stores import ElasticsearchDocumentStore
from haystack import Pipeline

# GenerativeQAPipeline
# ExtractiveQAPipeline with and without BM25 
# preprocess docs
# With question summary 
# With question sections
# With answer summary 
# With answer sections
#def csv_to_doc(path: str, **kwargs)

class WikiQA():
    def __init__(self, wiki_csv: str):
        self.wiki_csv = wiki_csv
        

    def create_reader(self, qa_model: str):
        self.qa_model = qa_model
        self.reader = FARMReader(model_name_or_path=qa_model,
                                 context_window_size=250,
                                 max_query_length=128,
                                 doc_stride = 72,
                                 top_k=2, use_gpu=True,)
    
    def prepare_csv(self, target_column: str):
        # Target column can be question/answer + summary/section
        df = pd.read_csv(self.wiki_csv)
        df = df.reset_index()
    

        

def WikiQA()
qa_model = 'deepset/roberta-base-squad2'
reader = FARMReader(model_name_or_path=qa_model,
                    context_window_size=250,
                    max_query_length=128,
                    doc_stride = 72,
                    top_k=2, use_gpu=True)


df = pd.read_csv('data/generated_QA_wiki.csv')
df = df.reset_index()
df.columns

df = df[['index', 'generated_question', 'generated_answer', 'question_wiki_summary']]
df = (df
      .fillna('No content')
      .replace(nan, 'No content'))
df['meta'] = df.apply(lambda x: {'question': x['generated_question'],
                                 'answer': x['generated_answer'],
                                 'index': x['index']},
                                axis=1).to_list()
df['content'] = df['question_wiki_summary']
df = df[['content', 'meta']]
#df.iloc[0]['meta']
df['id_hash_keys'] = [['meta', 'content']]*len(df)
df.iloc[0]['id_hash_keys']
dict_df = df.to_dict('records')

index = 'wiki_q_summary'

doc_store = helper.add_to_docstore(docs=dict_df, index=index, delete_docs=True)
docs = helper.load_all_docs(topic=index)
#docs[0]
#len(docs)

filtered_docs = [doc_store.get_all_documents(index=index, filters={'index': i}) for i in range(len(docs))]
queries = [docs[i].meta['question'] for i in range(len(docs))]
actual_answers = [docs[i].meta['answer'] for i in range(len(docs))]
len(queries)

pipeline = Pipeline()
pipeline.add_node(component=reader, name='Reader', inputs=['Query'])
results = pipeline.run_batch(queries=queries, documents=filtered_docs, debug=True)

wiki_ans = []
wiki_score = []
for val in results['answers']:
    wiki_ans.append([ans.answer for ans in val])
    wiki_score.append([ans.score for ans in val])
len(wiki_ans)
len(wiki_score)
df_wiki = pd.DataFrame(data={'generated_question': queries,
                        'generated_answer': actual_answers,
                        'wiki_answers': wiki_ans,
                        'wiki_scores': wiki_score})
df_wiki.to_csv('data/wiki_ques_summary_QA.csv', index=False)


wiki_ans = []
wiki_score = []
for answer in results['answers']:
    #print(len(answer))
    wiki_ans.append([ans.answer for ans in answer])
    wiki_score.append([ans.score for ans in answer])
    #print(answer.answer, answer.score)
    #print(answer, end='\n--\n')

for answer, document in zip(results['answers'], results['documents']):
    print(answer, document)    
docs
docs[0]


