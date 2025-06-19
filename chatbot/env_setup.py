import os
import dotenv
import firebase_admin
from firebase_admin import credentials, firestore

dotenv.load_dotenv(".env")

cred = credentials.Certificate("hydraq-chat-history.json")
firebase_admin.initialize_app(cred)
client = firestore.client()

CHAT_MODEL = os.getenv("CHAT_MODEL")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")
EMBEDDINGS_MODEL = os.getenv("EMBEDDINGS_MODEL")