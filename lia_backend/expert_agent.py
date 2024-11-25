import vertexai
from vertexai.generative_models import GenerativeModel
import vertexai.preview.generative_models as generative_models
from langchain_core.prompts import PromptTemplate
from langchain_google_community import GCSDirectoryLoader
from langchain.chains import RetrievalQA
from langchain_google_vertexai import VertexAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_google_vertexai import VertexAI

def generate_exp_ans_cot(question, retrieval_qa):
    template = f"""
    ```Answer the following interview question as a data scientist with 5 years of experience.  Provide a clear, concise, and well-structured explanation.  Explain its purpose, methodology, and common applications, including any relevant considerations or limitations. Do not make us of formatting (e.g., bullet points, italics for emphasis). ```

    Question: {question}

    """

    expert_prompt = template

    answer = retrieval_qa({"query": expert_prompt})

    return answer['result']


# testing
# import interview_processor

# print(generate_exp_ans_cot("What is PCA",interview_processor.retrievalQA()))