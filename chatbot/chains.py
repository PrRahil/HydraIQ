from langchain_core.output_parsers import StrOutputParser
from operator import itemgetter

from chatbot.llm_setup import llm
from chatbot.vector_store_setup import retriever
from chatbot.utils import reciprocal_rank_fusion, format_docs
from chatbot.prompts import standalone_question_prompt, multiquery_generation_prompt, answer_prompt

standalone_question_chain = ( standalone_question_prompt | llm | StrOutputParser() )

multiquery_generation_chain = ( multiquery_generation_prompt | llm | StrOutputParser() | (lambda x: x.split("\n")) )

rag_chain = (
    {
        "question": itemgetter("question"),
        "context": itemgetter("question") | standalone_question_chain | retriever | format_docs,
        "chat_history": itemgetter("chat_history")
    }
    | answer_prompt
    | llm
    | StrOutputParser()
)