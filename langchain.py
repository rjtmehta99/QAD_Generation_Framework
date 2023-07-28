from langchain.document_loaders import Docx2txtLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma
from sentence_transformers import SentenceTransformer
from langchain.embeddings import SentenceTransformerEmbeddings

model_kwargs = {'device': 'cuda'}
embed_model = SentenceTransformerEmbeddings(model_name='all-MiniLM-L6-v2', model_kwargs=model_kwargs)

# load documents
loader = Docx2txtLoader(r'/home/rjt/QA_LLM_Experiments/data/2022_Annual_Report.docx')
data = loader.load()

# chunk documents
text_splitter = CharacterTextSplitter(separator='\n\n', chunk_size=1000, chunk_overlap=50)
docs = text_splitter.split_documents(data)

# Vector DB
vector_db = Chroma.from_documents(docs, embed_model)

# Find related docs
query = 'how is microsoft earning trust?'
docs = vector_db.similarity_search(query)
len(docs)
docs[0].page_content