import pandas as pd
from haystack.document_stores import ElasticsearchDocumentStore
from haystack.schema import Document
from numpy import nan
from haystack.nodes import BM25Retriever, EmbeddingRetriever, TransformersDocumentClassifier
import gc

def csv_to_doc(path: str, **kwargs) -> dict[str, list[str]]:
    df = pd.read_csv(path)
    if 'source' in kwargs:
        # TODO - mention in readme.md to remove this code if all lines have to be used.
        df = df.head(50)
        content = kwargs['content']
        df['meta'] = ''
        df = df[[content, 'meta']]
        dict_df = df.to_dict('records')
        return dict_df

    title = kwargs['title']
    subject = kwargs['subject']
    content = kwargs['content']
    df[title] = df[title].replace('\d+\.\d+', '', regex=True)
    df = df[[title, subject, content]]
    df = (df
          .fillna('No content')
          .replace(nan, 'No content'))
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


def load_all_docs(topic: str) -> list[Document]:
    doc_store = ElasticsearchDocumentStore(index=topic)
    docs = doc_store.get_all_documents()
    return docs


def load_bm25_docs(topic: str, retrieval_query: str) -> list[Document]:
    doc_store = ElasticsearchDocumentStore(index=topic)
    retriever = BM25Retriever(document_store=doc_store)
    docs = retriever.retrieve(query=retrieval_query)
    return docs


def load_embedded_docs(topic: str, emb_retrieval_query: str) -> list[Document]: 
    doc_store = ElasticsearchDocumentStore(index=topic, similarity='dot_product', embedding_dim=768)
    retriever = EmbeddingRetriever(document_store=doc_store, embedding_model='sentence-transformers/msmarco-distilbert-base-v4',
                                   model_format='sentence_transformers')
    doc_store.update_embeddings(retriever=retriever)
    docs = retriever.retrieve(query=emb_retrieval_query)
    del retriever
    gc.collect()
    return docs


def split_labels(labels):
    labels = labels.split(',')
    labels = [label.strip() for label in labels]
    return labels


def load_zeroshot_docs(topic: str, zero_shot_query: str) -> list[Document]:
    # Clean input from dashboard
    #zero_shot_classes = zero_shot_query.split(',')
    #zero_shot_classes = [value.strip() for value in zero_shot_classes]
    zero_shot_labels = split_labels(zero_shot_query)
    # Filtering ES data
    _filter = {"classification.label": zero_shot_labels}
    doc_store = ElasticsearchDocumentStore(index=topic)
    docs = doc_store.get_all_documents(filters=_filter)
    return docs


def prepare_qa_string(df_gen_qa, **kwargs):
    if kwargs['retrieval_flag']:
        qa_output_str = f'BM25 - {len(df_gen_qa)} QA pairs were generated using documents filtered on "{kwargs["retrieval_flag"]}". Download the file below.'
    elif kwargs['emb_retrieval_flag']:
        qa_output_str = f'Embedding retrieval - {len(df_gen_qa)} QA pairs were generated using documents filtered on "{kwargs["emb_retrieval_query"]}". Download the file below.'
    elif kwargs['zero_shot_flag']:
        qa_output_str = f'Zero shot label - {len(df_gen_qa)} QA pairs were generated using documents filtered on "{kwargs["zero_shot_query"]}". Download the file below.'
    else:
        qa_output_str = f'{len(df_gen_qa)} QA pairs were generated. Download the file below.'
    return qa_output_str
