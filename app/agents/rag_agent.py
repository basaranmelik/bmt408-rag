from langchain_core.runnables import Runnable
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_qdrant import QdrantVectorStore as Qdrant
from config.qdrant_client import client, EMBEDDING_MODEL
from config.llm_config import LLM_MODEL

# Girilen vectorerstore collectionını context olarak alıp sorulan soruyu bu contexte göre cevaplar

def get_rag_agent(collection_name: str) -> Runnable:
    retriever = Qdrant(
        collection_name=collection_name,
        embedding=EMBEDDING_MODEL,
        client=client
    ).as_retriever()

    system_template = """
You are {historical_figure_name}. You must answer all questions from your own first-person perspective.
You are speaking directly to the user.

--- START OF IMPORTANT RULES ---
**You MUST answer ONLY in Turkish. Bu kural kesindir ve her koşulda geçerlidir.**
Never say "Based on the text provided", "According to the context", or any similar phrase that reveals you are using a document. You are {historical_figure_name}, and this knowledge is your own.
--- END OF IMPORTANT RULES ---

To help you answer, you have the following relevant memories and knowledge from your life.

--- Relevant Memories & Knowledge ---
{context}
--- End of Memories & Knowledge ---

When the user asks you a question, you MUST use the information from your "Relevant Memories & Knowledge" to form your response.
Act as if you are recalling these facts from your own experience.
"""

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_template),
            # --- Sohbet geçmişi için yer tutucu ---
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{question}"),
        ]
    )

    class RetrieverRunnable(Runnable):
        def invoke(self, input_dict, config=None, **kwargs):
            docs = retriever.get_relevant_documents(input_dict["question"])
            context = "\n\n".join([doc.page_content for doc in docs])
            # Gelen tüm girdileri bir sonraki adıma aktar
            return {
                "context": context,
                "question": input_dict["question"],
                "historical_figure_name": input_dict["historical_figure_name"],
                "chat_history": input_dict.get("chat_history", [])
            }

    retriever_runnable = RetrieverRunnable()

    rag_chain: Runnable = (
        retriever_runnable
        | prompt
        | LLM_MODEL
        | StrOutputParser()
    )
    
    return rag_chain