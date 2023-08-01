import pandas as pd
from pprint import pprint
from tqdm.auto import tqdm
from haystack.nodes import QuestionGenerator, BM25Retriever, FARMReader, TransformersDocumentClassifier
from haystack.document_stores import ElasticsearchDocumentStore
from haystack.pipelines import RetrieverQuestionGenerationPipeline, QuestionAnswerGenerationPipeline
from haystack.utils import print_questions

def openstax_to_doc(path:str) -> dict[str, list[str]]:
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

def add_to_docstore(docs:dict[str, list[str]], index:str, delete_docs:bool=False) -> None:
    # Initialize document store and write in the documents
    doc_store = ElasticsearchDocumentStore(index=index)
    if delete_docs:
        # Clear documents from previous runs
        doc_store.delete_documents(index=index)
    # Write documents from current execution
    doc_store.write_documents(docs)
    return doc_store

def classify_docs(labels:list[str], doc_store, index:str) -> None:
    classifier = TransformersDocumentClassifier(task='zero-shot-classification',
                                                model_name_or_path='MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli',
                                                labels=labels, use_gpu=True)
    docs = doc_store.get_all_documents(index=index)
    docs = classifier.predict(docs)
    doc_store.write_documents(docs, index=index)
    return doc_store
    