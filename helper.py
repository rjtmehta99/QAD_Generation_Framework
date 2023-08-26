import pandas as pd
from haystack.document_stores import ElasticsearchDocumentStore
from haystack.nodes import TransformersDocumentClassifier
import gc

'''
def openstax_to_doc(path: str) -> dict[str, list[str]]:
    """
    Convert Openstax dataframe to dict which can be passed as Document to Haystack
    """
    df = pd.read_csv(path)
    df['summary_heading'] = df['summary_heading'].replace('\d+\.\d+ ', '', regex=True)
    df.columns = ['topic', 'content', 'subject']
    df['meta'] = df.apply(lambda x: {'topic': x['topic'], 'subject': x['subject']}, axis=1).to_list()
    df = df[['content', 'meta']]
    dict_df = df.to_dict('records')
    return dict_df
'''

def csv_to_doc(path: str, **kwargs) -> dict[str, list[str]]:
    df = pd.read_csv(path)
    #title = column_dict['title']
    title = kwargs['title']
    subject = kwargs['subject']
    content = kwargs['content']
    df[title] = df[title].replace('\d+\.\d+', '', regex=True)
    df = df[[title, subject, content]]
    df['meta'] = df.apply(lambda x: {'topic': x[title], 'subject': x[subject], 'content': x[content]}, axis=1).to_list()
    df = df[[content, 'meta']]
    df.columns = ['content', 'meta']
    dict_df = df.to_dict('records')
    return dict_df


def add_to_docstore(docs: dict[str, list[str]], index: str, delete_docs: bool = False) -> None:
    """
    Initialize Elasticsearch document store and write the documents for given index.
    """
    doc_store = ElasticsearchDocumentStore(index=index)
    if delete_docs:
        doc_store.delete_documents(index=index)
    doc_store.write_documents(docs)
    return doc_store


def classify_docs(labels:list[str], doc_store, index: str) -> None:
    """
    Use Zero Shot Classification model to add labels to document.
    Labels added to the metadata for each document.
    """
    classifier = TransformersDocumentClassifier(task='zero-shot-classification',
                                                model_name_or_path='MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli',
                                                labels=labels, use_gpu=True)
    docs = doc_store.get_all_documents(index=index)
    docs = classifier.predict(docs)
    doc_store.write_documents(docs, index=index)
    return doc_store


def run_pipeline(pipeline, docs:dict[str, list[str]]) -> pd.DataFrame:
    """
    Run QA Generation Haystack pipeline. Remove QA pairs with answer confidence less than threshold.
    
    Args:
        pipeline: QA generation pipeline
        docs: Documents from Elasticsearch doc store 
    
    Returns:
        df (pd.DataFrame): DF containing generated QA and context document
    """
    generated_ques = []
    generated_ans = []
    doc_contexts = []

    results = pipeline.run(documents=docs)
    for query_content, answer_content, document_content in zip(results['queries'], results['answers'], results['documents']):
        answer = answer_content[0]
        document = document_content[0]
        if answer.score > 0.75:
            generated_ques.append(query_content)
            generated_ans.append(answer.answer)
            doc_contexts.append(document.content)
    df = pd.DataFrame(data={'generated_question':generated_ques, 'generated_answer':generated_ans, 'document_context':doc_contexts})
    del pipeline
    gc.collect()
    return df

