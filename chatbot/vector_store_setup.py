from pinecone import Pinecone
from langchain_pinecone import PineconeVectorStore

from chatbot.env_setup import PINECONE_API_KEY, PINECONE_INDEX_NAME
from chatbot.llm_setup import embeddings

pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(PINECONE_INDEX_NAME)
vector_store = PineconeVectorStore(index=index, embedding=embeddings)
retriever = vector_store.as_retriever(search_kwargs={"k": 25})