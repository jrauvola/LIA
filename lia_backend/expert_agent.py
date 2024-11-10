import vertexai
from vertexai.generative_models import GenerativeModel
import vertexai.preview.generative_models as generative_models
from langchain_core.prompts import PromptTemplate
from langchain_google_community import GCSDirectoryLoader
from langchain.chains import RetrievalQA
from langchain_google_vertexai import VertexAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain_google_vertexai import VertexAI

def generate_exp_ans_cot(question, retrieval_qa):
    template = f"""Context: ```You are a candidate interviewing for a data science role. Your goal is to provide clear, concise, and logically structured answers.```
                   Prompt: *** Answer each interview question directly and professionally, following these internal steps to derive your final answer (do not show the steps in your answer).
                   - Clarify the question: Restate internally to ensure understanding. If ambiguous, assume reasonable interpretations.
                   - Break down the problem: Identify key methods, concepts, or considerations involved (e.g., feature engineering, model selection).
                   - Apply domain knowledge: Use relevant data science principles such as statistics, machine learning, or data processing, referencing practical methods and terminology.
                   - Explain reasoning: Map out your approach mentally, considering trade-offs or alternatives, but only show the final answer.
                   - Use examples when relevant: Support your answer with practical examples or experience to illustrate your points, if appropriate.
                   - Summarize: Conclude with a brief summary that directly addresses the question and emphasizes key insights. 

                   Aim to give a well-developed paragraph or 200-300 words for the final answer. ***

                   Question: {question}
                   """

    expert_prompt = template

    answer = retrieval_qa({"query": expert_prompt})

    return answer['result']