import gc
import helper
import constants
import pandas as pd
import gradio as gr
from haystack.pipelines import QuestionAnswerGenerationPipeline
from haystack.nodes import QuestionGenerator, FARMReader

selected_rows = []

def init_pipeline():
    question_generator = QuestionGenerator(model_name_or_path='valhalla/t5-base-e2e-qg',
                                            max_length=420, split_length=75, 
                                            split_overlap=20, use_gpu=True)
    #qa_model = 'deepset/deberta-v3-large-squad2'
    qa_model = 'deepset/roberta-base-squad2'
    reader = FARMReader(model_name_or_path=qa_model,
                        top_k=1, use_gpu=True)
    pipeline = QuestionAnswerGenerationPipeline(question_generator, reader)
    return pipeline

def upload_csv(topic, file, labels, data_source, subject_filter):
    """
    Load CSV to Elasticsearch document store and apply zero shot classification.
    """
    print('Uploading CSV')
    gr.Info(f'Uploading file to Elasticsearch. Please wait.')
    if subject_filter != '':
        
        if subject_filter == 'Physics':
            docs = helper.csv_to_doc(path=constants.PHYSICS_CSV, source='subject',
                                    content='content')
        elif subject_filter == 'Chemistry':
            docs = helper.csv_to_doc(path=constants.CHEMISTRY_CSV, source='subject',
                                    content='content')
        elif subject_filter == 'Biology':
            docs = helper.csv_to_doc(path=constants.BIOLOGY_CSV, source='subject',
                                    content='content')
        elif subject_filter == 'Economics':
            docs = helper.csv_to_doc(path=constants.ECONOMICS_CSV, source='subject',
                                    content='content')
        elif subject_filter == 'Physical Science':
            docs = helper.csv_to_doc(path=constants.PHYSICAL_SCIENCE_CSV, source='subject',
                                    content='content')
    
    # Change options to source + subject combination. 
    if data_source == 'OpenStax.org (Biology)':
        #docs = helper.openstax_to_doc(path=file.name)
        docs = helper.csv_to_doc(path=constants.BIOLOGY_OSTAX_CSV, title='summary_heading', 
                                 subject='subject', content='summary_text')
    elif data_source == 'CK12.org (Biology)':
        docs = helper.csv_to_doc(path=constants.BIOLOGY_CK12_CSV, title='title',
                                 subject='subject', content='content')
    elif data_source == 'Brightstorm (Biology)':
        docs = helper.csv_to_doc(path=constants.BIOLOGY_BSTORM_CSV, title='title',
                                 subject='subject', content='summary')
    elif data_source == 'Others (Biology)':
        docs = helper.csv_to_doc(path=file.name, source='others', title='', subject='',
                                 content='content')
    '''
    if data_source == 'OpenStax.org':
        #docs = helper.openstax_to_doc(path=file.name)
        docs = helper.csv_to_doc(path=file.name, title='summary_heading', 
                                 subject='subject', content='summary_text')
    elif data_source == 'CK12.org':
        docs = helper.csv_to_doc(path=file.name, title='title',
                                 subject='subject', content='content')
    elif data_source == 'Brightstorm':
        docs = helper.csv_to_doc(path=file.name, title='title',
                                 subject='subject', content='summary')
    elif data_source == 'Others':
        docs = helper.csv_to_doc(path=file.name, source='others', title='', subject='',
                                 content='content')
    '''
    
    doc_store = helper.add_to_docstore(docs, index=topic, delete_docs=True)
    if labels != '':
        labels = helper.split_labels(labels)
        doc_store = helper.classify_docs(labels=labels, doc_store=doc_store, index=topic)
        return [gr.update(value=f'CSV added to Elasticsearch under {topic}.\nLabels added.', 
                          visible=True),
                gr.update(visible=True),
                gr.update(visible=True),
                gr.update(visible=True),
                gr.update(visible=True)]

    return [gr.update(value=f'CSV added to Elasticsearch under {topic}.', visible=True),
            gr.update(visible=True),
            gr.update(visible=True),
            gr.update(visible=True),
            gr.update(visible=True)]


def generate_qa_pairs(topic: str, retrieval_query: str, emb_retrieval_query: str, zero_shot_query: str):
    """
    Generate QA pair on the uploaded CSV.  
    
    If query passed, filter documents based on BM25 retrieval, embedding based retrieval 
    or filtered on the basis of generated Zero Shot label.
    
    Save generated QA pairs to CSV.
    """
    print('Generating QA Pairs')
    gr.Info('Generating QA Pairs. Please wait.')
    retrieval_flag = False
    emb_retrieval_flag = False
    zero_shot_flag = False

    global selected_rows
    selected_rows = []

    if retrieval_query == '' and emb_retrieval_query == '' and zero_shot_query == '':
        retrieval_flag = False
        docs = helper.load_all_docs(topic)

    elif retrieval_query != '' and emb_retrieval_query == '':
        retrieval_flag = True
        docs = helper.load_bm25_docs(topic, retrieval_query)

    elif emb_retrieval_query != '' and retrieval_query == '':
        emb_retrieval_flag = True
        docs = helper.load_embedded_docs(topic, emb_retrieval_query)

    elif retrieval_query == '' and emb_retrieval_query == '' and zero_shot_query != '':
        zero_shot_flag = True
        docs = helper.load_zeroshot_docs(topic, zero_shot_query)
        
    global df_gen_qa
    pipeline = init_pipeline()
    df_gen_qa = helper.run_pipeline(pipeline, docs)
    path = f'data/{topic}_generated_QA.csv'
    df_gen_qa.to_csv(path, index=False)
    kwargs = {'retrieval_flag': retrieval_flag, 'emb_retrieval_flag': emb_retrieval_flag, 
              'zero_shot_flag': zero_shot_flag, 'retrieval_query': retrieval_query, 
              'emb_retrieval_query': emb_retrieval_query, 'zero_shot_query': zero_shot_query}
    qa_output_str = helper.prepare_qa_string(df_gen_qa, **kwargs)

    # Dataframe that would contain selected rows
    # Initialized here to clean it before QA generated
    df_rows = pd.DataFrame(columns=['generated_question', 'generated_answer', 'document_context'])
    #path = f'data/{topic}_selected_QA.csv'
    #df_rows.to_csv(path, index=False)
    del pipeline
    gc.collect()
    
    return [gr.update(value=qa_output_str, visible=True),
            gr.update(value=path, visible=True),
            gr.update(value=df_gen_qa, visible=True),
            gr.update(visible=True), 
            gr.update(visible=True),
            gr.update(visible=True), 
            gr.update(value=df_rows, visible=True)]


def generate_distractors(topic, distractor_count):
    gc.collect()
    #df = pd.read_csv(file.name)
    df = pd.read_csv(constants.SELECTED_ROWS_CSV)
    df = df.drop(labels='document_context', axis=1)
    
    print('Generating distractors')
    distractor_count = int(distractor_count)
    
    gc.collect()
    # Rare usage, importing here to prevent memory overload by Word2Vec and LLMs simultaneously
    import distractor_generation
    gr.Info('Generating distractors')
    df['distractors'] = df['generated_answer'].apply(lambda x: 
                                                    distractor_generation.generate_disctractors(answer=x, 
                                                                                                distractor_count=distractor_count))
    # Convert string numeric answer with int numeric answer
    df['generated_answer'] = df['generated_answer'].apply(lambda x: distractor_generation.convert_numeric_answer(answer=x))
    # Code taken from https://stackoverflow.com/questions/43752845/list-of-values-to-columns-in-pandas-dataframe
    df_distractor = pd.DataFrame(df['distractors'].values.tolist()).add_prefix(constants.COL_PREFIX)
    df_distractor = df_distractor.join(df[constants.DIST_COLS])
    # Reorder columns
    df_distractor = df_distractor[constants.DIST_COLS+[constants.COL_PREFIX+str(_) for _ in range(distractor_count)]]
    
    path = f'data/{topic}_gen_QA_distractor.csv'
    df_distractor.to_csv(path, index=False)
    
    return [gr.update(value=path, visible=True), gr.update(value=path, visible=True)]


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
    #path = f'data/selected_data.csv'
    df_select.to_csv(constants.SELECTED_ROWS_CSV, index=False)
    return [gr.update(value=constants.SELECTED_ROWS_CSV), gr.update(value=constants.SELECTED_ROWS_CSV)] 


def notify_subj_file(subject):
    # Notify on subject change from dropdown
    gr.Info(f'File added for {subject}, click upload to begin.')


def enable_upload(event: gr.SelectData):
    if event.value == 'Others':
        return [gr.update(visible=True), gr.update(visible=False)]
    else:
        return [gr.update(visible=False), gr.update(visible=True)]


theme = gr.themes.Soft()
with gr.Blocks(css=constants.css, title=constants.tab_title, theme=theme) as dashboard:
    gr.HTML(constants.page_title)
    with gr.Row():
        topic = gr.Textbox(label='Topic', 
                           placeholder='openstax_biology, ck12_economics...')
        data_source = gr.Dropdown(choices=['OpenStax.org (Biology)', 'CK12.org (Biology)',
                                           'Brightstorm (Biology)', 'Others'],
                                  label='Data Source')
        subject_filter = gr.Dropdown(choices=['Physics (All)', 'Chemistry (All)', 'Biology (All)', 
                                              'Economics (All)', 'Physical Science (All)'],
                                    label='Subject')
        subject_filter.change(fn=notify_subj_file, inputs=subject_filter)
        labels = gr.Textbox(label='Zero Shot Labels', 
                            placeholder= 'Add labels (use , to split)')
    
    file = gr.File(file_types=['csv'], label='Add CSV', visible=False)
    topic.change(fn=change_label, inputs=topic, outputs=file)    
    
    data_source.select(fn=enable_upload, inputs=None, outputs=[file, subject_filter])
    upload_btn = gr.Button('Add Data')
    data_output_box = gr.Textbox(label='Data Upload Status', visible=False)
    
    with gr.Row():
        retrieval_query = gr.Textbox(label='Retrieval Query - BM25', placeholder='Enter query', 
                                    visible=False)
        emb_retrieval_query = gr.Textbox(label='Retrieval Query - Embedding based', placeholder='Enter query',
                                        visible=False)
        zero_shot_query = gr.Textbox(label='Zero Shot Label', placeholder='Enter labels (use , to split)',
                                    visible=False)

    generate_qa_btn = gr.Button(f'Generate Question Answer Pairs', visible=False)

    upload_btn.click(fn=upload_csv,
                    inputs=[topic, file, labels, data_source, subject_filter], 
                    outputs=[data_output_box, generate_qa_btn, retrieval_query, 
                            emb_retrieval_query, zero_shot_query])

    qa_output_box = gr.Textbox(label='Generated QA Pairs Status', visible=False)
    generated_file = gr.File(label='Generated CSV', visible=False)
    df_output = gr.Dataframe(label='Generated QA Pairs', visible=False, wrap=True, 
                             show_label=True, interactive=False)
    
    selected_rows_file = gr.File(label='Selected Rows', visible=False)
    df_rows = gr.DataFrame(label='Selected Rows', visible=False, wrap=True,
                           show_label=True, interactive=False)
    
    #distractor_file = gr.File(label='Add CSV to generate distractors', visible=False, file_types=['csv'])
    distractor_count = gr.Number(label='Distractor Answer Count', value=5 , visible=False)

    generate_distr_btn = gr.Button(value='Generate Distractor Answers From Selected Rows', visible=False)
    generated_distr_file = gr.File(label='Generated QA Distractor Answers CSV', visible=False)
    
    generate_qa_btn.click(fn=generate_qa_pairs, 
                          inputs=[topic, retrieval_query, emb_retrieval_query, zero_shot_query], 
                          outputs=[qa_output_box, generated_file, df_output, selected_rows_file, 
                                   generate_distr_btn, distractor_count, df_rows])

    df_output.select(fn=add_row, inputs=None, outputs=[selected_rows_file, df_rows])

    df_distr = gr.DataFrame(label='Generated Distractor Answers', visible=False, wrap=True,
                            show_label=True, interactive=False)
    generate_distr_btn.click(fn=generate_distractors,
                            inputs=[topic, distractor_count],
                            outputs=[generated_distr_file, df_distr])

dashboard.queue().launch(server_port=8080, share=False)
