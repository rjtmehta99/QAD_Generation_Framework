import gradio as gr
import pandas as pd
import helper
from haystack.nodes import QuestionGenerator, FARMReader
from haystack.pipelines import QuestionAnswerGenerationPipeline
from haystack.document_stores import ElasticsearchDocumentStore

def upload_csv(topic, file, labels, data_source):
    print('Uploading')
    if data_source == 'OpenStax.org':
        docs = helper.openstax_to_doc(path=file.name)
    else:
        raise NotImplementedError
    
    doc_store = helper.add_to_docstore(docs, index=topic, delete_docs=True)
    if labels != '':
        labels = labels.split(',')
        labels = [label.strip for label in labels]
        doc_store = helper.classify_docs(labels=labels, doc_store=doc_store, index=topic)
        return [f'CSV added to Elasticsearch under {topic}.\nLabels added.', 
                gr.update(visible=True),
                gr.update(visible=True)]

    return [f'CSV added to Elasticsearch under {topic}.', 
            gr.update(visible=True),
            gr.update(visible=True)]


def generate_qa_pairs(topic):
    question_generator = QuestionGenerator(model_name_or_path='valhalla/t5-base-e2e-qg',
                                       max_length=420, split_length=75, 
                                       split_overlap=20, use_gpu=True)
    reader = FARMReader(model_name_or_path="deepset/roberta-base-squad2", 
                    top_k=1, use_gpu=True)
    pipeline = QuestionAnswerGenerationPipeline(question_generator, reader)
    doc_store = ElasticsearchDocumentStore(index=topic)
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


with gr.Blocks() as demo:
    with gr.Row():
        topic = gr.Textbox(label='Topic', placeholder='openstax_biology, ck12_economics...')
        data_source = gr.Dropdown(["OpenStax.org", "CK12.org", "Brightstorm"], label="Data Source")
        labels = gr.Textbox(label='Zero Shot Labels', placeholder= 'Add labels science, economics, technology...(use , to split)')
    file = gr.File(file_types=['csv'], label='Add CSV for topic')
    upload_btn = gr.Button('Upload')
    output_box = gr.Textbox(label='', value='', visible=False)
    generate_qa_btn = gr.Button(f'Generate {topic} Question Answer Pairs', visible=False)
    upload_btn.click(fn=upload_csv, inputs=[topic, file, labels, data_source], outputs=[output_box, output_box, generate_qa_btn])

    generate_qa_btn.click(fn=generate_qa_pairs, inputs=[topic], outputs=[])
demo.launch()

# TODO - 
# change output in gen_qa_pairs on status update
# display generated qa pair df
#
# 1. data loader for all formats.
# 2. TDQMs
# 3. Option to choose different models in dashboard
# 4. Set visibility to False for output_box, later True.
# 5. Add data filtering (via class labels)
