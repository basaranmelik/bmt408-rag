import logging
from typing import List, Optional
from langchain_core.messages import BaseMessage
from langchain_qdrant import QdrantVectorStore as Qdrant
from config.qdrant_client import client, EMBEDDING_MODEL
from config.llm_config import LLM_MODEL
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field

logger = logging.getLogger(__name__)

VECTORSTORE_THRESHOLD = 0.5


class RelevanceCheck(BaseModel):
    is_relevant: bool = Field(description="True if the question is relevant to the character's domain, False otherwise.")


def is_question_relevant_to_character(historical_figure_name: str, contextual_question: str) -> bool:
    logger.info(f"Performing LLM relevance check for character '{historical_figure_name}'.")
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert at determining if a user's question is relevant to a specific character's domain..."),
        ("human", "The character is **{historical_figure_name}**. The user's question, including conversation history, is: **'{question}'**\n\nIs this question something that **{historical_figure_name}** could plausibly have an opinion on...?")
    ])
    structured_llm = LLM_MODEL.with_structured_output(RelevanceCheck)
    chain = prompt | structured_llm
    try:
        result = chain.invoke({"historical_figure_name": historical_figure_name, "question": contextual_question})
        logger.info(f"Relevance check result: {result.is_relevant}")
        return result.is_relevant
    except Exception as e:
        logger.error(f"Error during LLM relevance check: {e}")
        return False


def determine_route(
    figure_id: int,
    figure_name: str,
    collection_name: Optional[str],
    question: str,
    chat_history: List[BaseMessage]
) -> str:
    logger.info("--- ROUTING ---")
    history_str = "\n".join([f"{msg.type}: {msg.content}" for msg in chat_history])
    contextual_question = f"Previous Conversation:\n{history_str}\n\nLatest User Question: {question}"

    if collection_name:
        try:
            vector_store = Qdrant(client=client, collection_name=collection_name, embedding=EMBEDDING_MODEL)
            results = vector_store.similarity_search_with_score(query=contextual_question, k=1)
            if results and results[0][1] > VECTORSTORE_THRESHOLD:
                score = results[0][1]
                logger.info(f"Vector store score {score:.4f} > {VECTORSTORE_THRESHOLD}. Route: 'vectorstore'.")
                return "vectorstore"
            elif results:
                logger.info(f"Vector store score {results[0][1]:.4f} too low. Proceeding to relevance check.")
            else:
                logger.info("No documents found in vector store. Proceeding to relevance check.")
        except Exception as e:
            logger.warning(f"Could not check vector store '{collection_name}': {e}. Proceeding to relevance check.")
    else:
        logger.info("No collection found for figure. Proceeding to relevance check.")

    if is_question_relevant_to_character(figure_name, contextual_question):
        logger.info("Question is topically relevant. Route: 'websearch'.")
        return "websearch"
    else:
        logger.info("Question is not topically relevant. Route: 'reject'.")
        return "reject"
