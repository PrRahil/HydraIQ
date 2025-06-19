from langchain_community.chat_message_histories.firestore import FirestoreChatMessageHistory

from chatbot.env_setup import client
from chatbot.chains import rag_chain

def fetchChatHistory(user_id, session_id):
 message_history = FirestoreChatMessageHistory(
   collection_name=f"chat-history/users/{user_id}",
   session_id=session_id,
   user_id=user_id,
   firestore_client=client
 )
 return message_history

def chatWithChain(question, chat_history):
    chat_history.add_user_message(question)
    response = rag_chain.invoke({"question": question, "chat_history": chat_history.messages})
    # print("Streamming response...\n")
    return response
    # chunks = []
    # for chunk in rag_chain.stream({"question": question, "chat_history": chat_history.messages}):
    #     yield chunk
    #     chunks.append(chunk)
    # print("\n\nStreamming response done.")
    # response = "".join(chunks)
    chat_history.add_ai_message(response)
    # print("Chat history updated.")