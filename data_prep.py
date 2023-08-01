import helper
import pandas as pd
from pprint import pprint
from tqdm.auto import tqdm
from haystack.nodes import QuestionGenerator, BM25Retriever, FARMReader
from haystack.document_stores import ElasticsearchDocumentStore
from haystack.pipelines import RetrieverQuestionGenerationPipeline, QuestionAnswerGenerationPipeline
from haystack.utils import print_questions, export_answers_to_csv

# Openstax Biology
topic = 'openstax_biology'
docs = helper.openstax_to_doc(path='data/openstax_biology.csv')

doc_store = helper.add_to_docstore(docs, index=topic, delete_docs=True)
doc_store = helper.classify_docs(labels=['physics', 'chemistry', 'biology'],
                                doc_store=doc_store, index=topic)
question_generator = QuestionGenerator(model_name_or_path='valhalla/t5-base-e2e-qg',
                                       max_length=420, split_length=75, 
                                       split_overlap=20, use_gpu=True)
#reader = FARMReader(model_name_or_path="deepset/roberta-base-squad2", 
#                    use_gpu=True, confidence_threshold=0.70)
reader = FARMReader(model_name_or_path="deepset/roberta-base-squad2", 
                    top_k=1, use_gpu=True)
pipeline = QuestionAnswerGenerationPipeline(question_generator, reader)
docs = doc_store.get_all_documents()
results = pipeline.run(documents=docs)

generated_ques = []
generated_ans = []
doc_contexts = []
for query_content, answer_content, document_content in zip(results['queries'], results['answers'], results['documents']):
    answer = answer_content[0]
    document = document_content[0]
    if answer.score > 0.75:
        generated_ques.append(query_content)
        generated_ans.append(answer.answer)
        doc_contexts.append(document.content)

df_gen_qa = pd.DataFrame(data={'generated_question':generated_ques, 'generated_answer':generated_ans,
                               'document_context':doc_contexts})
df_gen_qa.to_csv(f'data/{topic}_generated_QA.csv', index=False)
