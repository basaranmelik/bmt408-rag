from langchain.chains import LLMChain
from langchain_core.prompts import PromptTemplate
from config.llm_config import LLM_MODEL

# PDF yüklenirken eklenen pdfin girilen karakterle alakalı olup olmadığını kontrol eden ajan
template = """
You are given a text from a PDF and a historical character's name.

Determine if the text is genuinely about that historical figure.

Character name: {historical_figure_name}
PDF text: {context}

Answer only with "YES" or "NO".
"""

prompt = PromptTemplate(
    template=template,
    input_variables=["historical_figure_name", "context"]
)

character_validation_chain = LLMChain(
    llm=LLM_MODEL,
    prompt=prompt
)
