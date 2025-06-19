from chatbot.chat_utils import fetchChatHistory, chatWithChain

chat_history = fetchChatHistory("user2", "session2")
response = chatWithChain('Hi', chat_history)