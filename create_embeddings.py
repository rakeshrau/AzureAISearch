# Import libraries
from common import *
from azure.search.documents.models import VectorizedQuery
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import AzureBlobStorageContainerLoader

# Load the pdf documents from the Azure Blob Storage (ADLS Gen 2)
loader = AzureBlobStorageContainerLoader(conn_str=blob_connection_string, container=blob_container_name)
pages = loader.load()
files = [file.metadata['source'].split(f"{blob_container_name}/")[1] for file in pages]
print(f"{len(files)} files are loaded")

# from_tiktoken_encoder enables use to split on tokens rather than characters
text_splitter = RecursiveCharacterTextSplitter(
   chunk_size=1000,
   chunk_overlap=100
)
docs = text_splitter.split_documents(pages)

try:
    searchindex = create_search_index(search_index_name)
    search_index_client.create_or_update_index(searchindex)
except Exception as e:
    print("Index is not created or updated", e)

for idx, file in enumerate(files):
    chunk_content = [chunk.page_content for chunk in docs if chunk.metadata["source"].endswith(file)]
    chunk_embeddings = embeddings_client.embed_documents(chunk_content)
    data = [
        {
            "FILE_ID": f"{file}_{idx}",
            "CHUNK_ID": f"{idx}_{i}",
            "CHUNK": chunk,
            "FILE_NAME": file,
            "CHUNK_VECTOR": chunk_embeddings[i]
        }
        for i, chunk in enumerate(chunk_content)
    ]

search_client = search_index_client.get_search_client(search_index_name)
search_client.upload_documents(data)
print("Uploaded chunks and embeddings for recursive text splitter")

# Pure Vector Search
query = "Is voclosporin better than Belimumab?"  
  
embedding = embeddings_client.embed_query(query)
vector_query = VectorizedQuery(vector=embedding, k_nearest_neighbors=3, fields="CHUNK_VECTOR")
  
results = search_client.search(  
    search_text=None,  
    vector_queries= [vector_query],
    select=["FILE_ID", "CHUNK_ID", "CHUNK", "FILE_NAME"],
    top=1
)

for result in results:  
    print(f"FILE_ID: {result['FILE_ID']}")  
    print(f"CHUNK_ID: {result['CHUNK_ID']}")
    print(f"FILE_NAME: {result['FILE_NAME']}")
    print(f"Score: {result['@search.score']}")  
    print(f"Content: {result['CHUNK']}") 
