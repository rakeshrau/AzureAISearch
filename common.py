# Import libraries
from langchain_openai import AzureOpenAIEmbeddings
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SearchField,
    SearchFieldDataType,
    VectorSearch,
    VectorSearchProfile,
    HnswAlgorithmConfiguration
)
import os
from dotenv import load_dotenv

load_dotenv(override=True) # take environment variables from .env.


# Get the secrets from Key Vault
secret_scope = "Secret-Scope-RxGblAKVDevTestBenGenAI"

# Variables not used here do not need to be updated in your .env file
azure_search_endpoint = os.environ["AZURE_SEARCH_SERVICE_ENDPOINT"]
azure_search_credential = AzureKeyCredential(os.environ["AZURE_SEARCH_ADMIN_KEY"])
search_index_name = os.environ["AZURE_SEARCH_INDEX"]
blob_connection_string = os.environ["BLOB_CONNECTION_STRING"]
blob_container_name = os.environ["BLOB_CONTAINER_NAME"]
azure_embedding_model_name = os.environ["AZURE_OPENAI_EMBEDDING_DEPLOYMENT"]
azure_openai_endpoint = os.environ["AZURE_OPENAI_ENDPOINT"]
azure_openai_api_version = os.environ["AZURE_OPENAI_API_VERSION"]
azure_openai_key = os.environ["AZURE_OPENAI_KEY"]

embeddings_client = AzureOpenAIEmbeddings(    
        azure_endpoint=azure_openai_endpoint,
        api_key=azure_openai_key,
        azure_deployment=azure_embedding_model_name,
        openai_api_version=azure_openai_api_version,
    )
    
# function to create or update the Azure search index if not present
def create_search_index(index_name):
    return SearchIndex(
        name=index_name,
        fields=[
            SearchField(
                name="CHUNK_ID",
                type=SearchFieldDataType.String,
                key=True,
                hidden=False,
                filterable=True,
                sortable=True,
                facetable=False,
                searchable=True,
                analyzer_name="keyword"
            ),
            SearchField(
                name="FILE_ID",
                type=SearchFieldDataType.String,
                hidden=False,
                filterable=True,
                sortable=True,
                facetable=False,
                searchable=True
            ),
            SearchField(
                name="CHUNK",
                type=SearchFieldDataType.String,
                hidden=False,
                filterable=False,
                sortable=False,
                facetable=False,
                searchable=True
            ),
            SearchField(
                name="FILE_NAME",
                type=SearchFieldDataType.String,
                hidden=False,
                filterable=False,
                sortable=False,
                facetable=False,
                searchable=True
            ),
            SearchField(
                name="CHUNK_VECTOR",
                type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                searchable=True, 
                vector_search_dimensions=1536, 
                vector_search_profile_name="myHnswProfile"
            )
        ],
        # Configure the vector search configuration  
        vector_search = VectorSearch(
            algorithms=[
                HnswAlgorithmConfiguration(
                    name="myHnsw"
                )
            ],
            profiles=[
                VectorSearchProfile(
                    name="myHnswProfile",
                    algorithm_configuration_name="myHnsw",
                )
            ]
        )
    )

search_index_client = SearchIndexClient(
    endpoint = azure_search_endpoint,
    credential = azure_search_credential
)
