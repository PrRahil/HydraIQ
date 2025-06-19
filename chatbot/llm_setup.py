from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.globals import set_llm_cache
from langchain_community.cache import InMemoryCache
from langchain_groq import ChatGroq

from chatbot.env_setup import OPENAI_API_KEY, CHAT_MODEL, EMBEDDINGS_MODEL

llm = ChatOpenAI(
    model=CHAT_MODEL,
    temperature=0.7,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    api_key=OPENAI_API_KEY,
)
# llm = ChatGroq(temperature=0.7, groq_api_key="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", model_name="llama3-8b-8192")
set_llm_cache(InMemoryCache())

embeddings = OpenAIEmbeddings(model=EMBEDDINGS_MODEL)
