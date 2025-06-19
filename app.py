from flask import Flask, jsonify, request, Response
import bs4
from langchain_community.document_loaders import WebBaseLoader
from flask_cors import CORS
from operator import itemgetter
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from chatbot.llm_setup import llm
from langchain_core.output_parsers import StrOutputParser


from chatbot.chat_utils import fetchChatHistory, chatWithChain
from chatbot.download_files import download_s3_bucket
from chatbot.access_files import get_files
from chatbot.filter import is_related_to_groundwater
# from data_setup.llm_extract import do_the_thing

app = Flask(__name__)
CORS(app)


# @app.route("/chat/prepare-dataset")
# def prepare():
#     # download_s3_bucket("abhi-bhingradiya-pvt", "./input")
#     files = get_files()
#     do_the_thing(files)
#     return jsonify({'message': 'Dataset prepared successfully'})

def non_groundwater_chain(user_input, chat_history):
    fallback_system_prompt = f"""
    You are a helpful chatbot focused on groundwater-related questions.
    If the user asks about something not related to groundwater (e.g., greetings or general queries),
    do not provide an answer based on knowledge. Instead, provide a polite response acknowledging the question
    without answering it directly, saying that you can only answer groundwater-related questions. Also if you are asked about anything personal about you, do not provide any information about yourself.
    User input: {user_input}
    Response:
    """

    fallback_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", fallback_system_prompt),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{question}"),
    ]
)

    # Construct the chain with the necessary parts
    fallback_chain = (
        {
            "question": itemgetter("question"),
            "chat_history": itemgetter("chat_history")
        }
        | fallback_prompt  # Add the prompt as part of the chain
        | llm  # Run through the language model
        | StrOutputParser()  # Parse the output as a string
    )

    return fallback_chain.invoke({"question": user_input, "chat_history": chat_history})


@app.route("/chat/<session_id>", methods=['GET', 'POST'])
def disp(session_id):
    input = request.get_json(force=True)
    user_id = input.get('user_id')
    user_input = input.get('user_input')

    if not input:
        return jsonify({'error': 'No user input provided'}), 400

    chat_history = fetchChatHistory(user_id, session_id)
    print(f"Chat History: {chat_history}")
    print(f"User Input: {user_input}")

    # if is_related_to_groundwater(user_input):
    #     print("Input is related to groundwater.")
    response = chatWithChain(user_input, chat_history)
    # else:
    #     print("Input is NOT related to groundwater.")
    #     response = non_groundwater_chain(user_input, chat_history.messages)

    return Response(response, content_type='text/plain')



@app.route("/chat/get-history/<session_id>", methods=['GET', 'POST'])
def hist(session_id):
    input = request.get_json(force=True)
    user_id = input.get('user_id')

    if not input:
        return jsonify({'error': 'No user input provided'}), 400

    chat_history = fetchChatHistory(user_id, session_id)
    # print(vars(chat_history.messages[0]))


    # Convert HumanMessage objects to a JSON-serializable format
    messages = [{"role": msg.type, "content": msg.content} for msg in chat_history.messages]

    return jsonify(messages)


if __name__ == '__main__':
    app.run(debug = True)