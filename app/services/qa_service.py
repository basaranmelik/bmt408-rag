import logging
from typing import List, Optional
from langchain_core.messages import BaseMessage
from agents.rag_agent import get_rag_agent
from agents.websearch_agent import get_websearch_agent
from agents.router_agent import determine_route

logger = logging.getLogger(__name__)


def answer_question(
    figure_id: int,
    figure_name: str,
    collection_name: Optional[str],
    question: str,
    chat_history: List[BaseMessage]
) -> str:
    logger.info(f"Answering question for figure='{figure_name}' (id={figure_id})")

    route = determine_route(figure_id, figure_name, collection_name, question, chat_history)
    logger.info(f"Determined route: {route}")

    if route == "vectorstore":
        logger.info(f"Using RAG agent with collection: {collection_name}")
        rag_agent = get_rag_agent(collection_name)
        answer = rag_agent.invoke({
            "question": question,
            "historical_figure_id": figure_id,
            "historical_figure_name": figure_name,
            "chat_history": chat_history
        })

    elif route == "websearch":
        logger.info(f"Using websearch agent for figure: {figure_name}")
        websearch_agent = get_websearch_agent()
        answer = websearch_agent.invoke({
            "question": question,
            "historical_figure_id": figure_id,
            "historical_figure_name": figure_name,
            "chat_history": chat_history
        })

    else:
        answer = f"Ben {figure_name}. Bu soru bilgi alanımın dışında, cevap veremiyorum."

    return answer
