import helper
import constants
import gradio as gr
from haystack.pipelines import QuestionAnswerGenerationPipeline
from haystack.document_stores import ElasticsearchDocumentStore
from haystack.nodes import QuestionGenerator, FARMReader, BM25Retriever

question_generator = QuestionGenerator(model_name_or_path='valhalla/t5-base-e2e-qg',
                                        max_length=420, split_length=75, 
                                        split_overlap=20, use_gpu=True)
reader = FARMReader(model_name_or_path='deepset/deberta-v3-large-squad2',
                    top_k=1, use_gpu=True)
pipeline = QuestionAnswerGenerationPipeline(question_generator, reader)
selected_rows = []

def upload_csv(topic, file, labels, data_source):
    """
    Load CSV to Elasticsearch document store and apply zero shot classification.
    """
    print('Uploading CSV')
    gr.Info(f'Uploading file to Elasticsearch. Please wait.')
    if data_source == 'OpenStax.org':
        docs = helper.openstax_to_doc(path=file.name)
    else:
        raise NotImplementedError
    
    doc_store = helper.add_to_docstore(docs, index=topic, delete_docs=True)
    if labels != '':
        labels = labels.split(',')
        labels = [label.strip() for label in labels]
        doc_store = helper.classify_docs(labels=labels, doc_store=doc_store, index=topic)
        return [gr.update(value=f'CSV added to Elasticsearch under {topic}.\nLabels added.', visible=True),
                gr.update(visible=True),
                gr.update(visible=True)]

    return [gr.update(value=f'CSV added to Elasticsearch under {topic}.', visible=True),
            gr.update(visible=True),
            gr.update(visible=True)]


def generate_qa_pairs(topic, retrieval_query):
    """
    Generate QA pair on the uploaded CSV.  
    If query passed, filter documents based on BM25 retrieval.
    Saves generated QA pairs to CSV.
    """
    print('Generating QA Pairs')
    gr.Info('Generating QA Pairs. Please wait.')
    doc_store = ElasticsearchDocumentStore(index=topic)
    if retrieval_query == '':
        retrieval_flag = False
        docs = doc_store.get_all_documents()
    else:
        retrieval_flag = True
        retriever = BM25Retriever(document_store=doc_store)
        docs = retriever.retrieve(query=retrieval_query)
    
    global df_gen_qa
    df_gen_qa = helper.run_pipeline(pipeline, docs)
    path = f'data/{topic}_generated_QA.csv'
    df_gen_qa.to_csv(path, index=False)

    if retrieval_flag:
        qa_output_str = f'{len(df_gen_qa)} QA pairs were generated using documents filtered on "{retrieval_query}". Download the file below.'
    else:
        qa_output_str = f'{len(df_gen_qa)} QA pairs were generated. Download the file below.'

    return [gr.update(value=qa_output_str, visible=True),
            gr.update(value=path, visible=True),
            gr.update(value=df_gen_qa, visible=True),
            gr.update(visible=True)]


def change_label(topic):
    # Change label based on input from user.
    return gr.update(label=f'Add {topic} CSV')


def add_row(event: gr.SelectData):
    """
    Save selected rows (from QA pair df) to CSV.
    This helps in quicker filtering of data for researchers.
    """
    print(f'{event.index[0]} row added')
    selected_rows.append(event.index[0])
    #selected_rows = list(set(selected_rows))
    df_select = df_gen_qa.iloc[selected_rows, :]
    path = f'data/selected_data.csv'
    df_select.to_csv(path, index=False)
    return gr.update(value=path)


theme = gr.themes.Soft()
with gr.Blocks(css=constants.css, title=constants.tab_title, theme=theme) as dashboard:
    gr.HTML(constants.page_title)
    with gr.Row():
        topic = gr.Textbox(label='Topic', 
                           placeholder='openstax_biology, ck12_economics...')
        data_source = gr.Dropdown(['OpenStax.org', 'CK12.org', 'Brightstorm'],
                                  label='Data Source')
        labels = gr.Textbox(label='Zero Shot Labels', 
                            placeholder= 'Add labels science, economics, technology...(use , to split)')
    
    file = gr.File(file_types=['csv'], label='Add CSV')
    topic.change(fn=change_label, inputs=topic, outputs=file)    
    upload_btn = gr.Button('Upload')
    data_output_box = gr.Textbox(label='Data Upload Status', visible=False)
    retrieval_query = gr.Textbox(label='Retrieval Query - BM25', placeholder='Enter query', 
                                 visible=False)
    generate_qa_btn = gr.Button(f'Generate Question Answer Pairs', visible=False)

    upload_btn.click(fn=upload_csv,
                    inputs=[topic, file, labels, data_source], 
                    outputs=[data_output_box, generate_qa_btn, retrieval_query])

    qa_output_box = gr.Textbox(label='Generated QA Pairs Status', visible=False)
    generated_file = gr.File(label='Generated CSV', visible=False)
    df_output = gr.Dataframe(label='Generated QA Pairs', visible=False, wrap=True, 
                             show_label=True, interactive=False)
    selected_rows_file = gr.File(label='Download selected rows', visible=False)
    
    generate_qa_btn.click(fn=generate_qa_pairs, 
                          inputs=[topic, retrieval_query], 
                          outputs=[qa_output_box, generated_file, df_output, selected_rows_file])    

    df_output.select(fn=add_row, inputs=None, outputs=selected_rows_file)

dashboard.queue().launch(server_port=8080, share=True)

# TODO - 
# change output in gen_qa_pairs on status update
# display generated qa pair df -> make it run for tqdm(run doc)
#
# 1. data loader for all formats.
# 2. TDQMs
# 3. Option to choose different models in dashboard
# 4. Set visibility to False for output_box, later True.
# 5. Add data filtering (via class labels)
# 6. Give option of selecting QA model
