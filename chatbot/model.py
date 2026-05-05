# chatbot/model.py
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq
from chatbot.prompt import CUSTOM_PROMPT


class ChatbotModel:
    """Chatbot model class to manage the LLM and interactions."""

    def __init__(self, api_key):
        self.llm = self.initialize_llm(api_key)
        self.memory = ConversationBufferMemory(input_key="question", memory_key="history")
        self.prompt = PromptTemplate(template=CUSTOM_PROMPT, input_variables=['history', 'context', 'question'])
        self.chain = self.create_chain()

    def initialize_llm(self, api_key):
        """Initialize the ChatGroq model with the provided API key."""
        return ChatGroq(
            api_key=api_key,
            model="llama-3.3-70b-versatile",
            temperature=0,
            max_tokens=None,
            timeout=None,
            max_retries=2,
        )

    def create_chain(self):
        """Create the LLM chain with memory using modern LCEL syntax."""
        return self.prompt | self.llm | StrOutputParser()

    def ask_chatbot(self, question):
        """Handle user questions and return responses."""
        history = self.memory.load_memory_variables({}).get("history", "")

        response = self.chain.invoke({
            "history": history,
            "context": "",
            "question": question
        })

        # Save the interaction to memory
        self.memory.save_context(
            {"question": question},
            {"output": response}
        )

        return response