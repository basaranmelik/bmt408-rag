from langchain_core.runnables import Runnable, RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.tools.tavily_search import TavilySearchResults
from config.llm_config import LLM_MODEL

# Girilen sorunun cevabını webde arayan ajan

def get_websearch_agent() -> Runnable:
    web_search_tool = TavilySearchResults(k=3, description="A tool for searching the modern web.")

    system_template = """
You are {historical_figure_name}. You are speaking directly to a user from the modern world.

--- START OF IMPORTANT RULES ---
**Your response MUST BE exclusively in Turkish. Cevabın kesinlikle Türkçe olmalıdır.**
Do NOT mention the web search, the internet, or the provided text.
--- END OF IMPORTANT RULES ---

You have been provided with up-to-date information from a web search to help you answer questions about topics you might not be familiar with.
Here is the information from the web search:

--- Web Search Results ---
{context}
--- End of Web Search Results ---

Your task is to integrate this new information with your own personality and perspective to answer the user's question.
Speak in your own voice as {historical_figure_name}.
"""

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_template),
            # --- Sohbet geçmişi için yer tutucu ---
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{question}"),
        ]
    )
    
    web_search_chain = (
        RunnablePassthrough.assign(
            context=lambda inputs: web_search_tool.invoke({"query": inputs["question"]})
        )
        | prompt
        | LLM_MODEL
        | StrOutputParser()
    )

    return web_search_chain