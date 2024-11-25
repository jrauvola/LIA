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

def generate_exp_ans_cot(question, retrieval_qa, interview_instance):
    template = f"""
    You are an experienced data scientist in a job interview. Answer the question naturally as if speaking to the interviewer, using your provided personal profile for context.

    Context:
    Personal Profile: {interview_instance.personal_profile}
    Question: {question}

    Guidelines for your response:
    - Speak in first person ("I", "my", "we")
    - Use natural transitions and connecting phrases
    - Keep it concise (150-200 words)
    - Include a brief opening statement that directly answers the question
    - Follow with a technical explanation using correct terminology
    - Share a specific example from your personal profile
    - Conclude with the business impact or practical application
    
    Response style:
    - Conversational and engaging, as if speaking in person
    - Professional but approachable
    - Show both technical expertise and communication skills
    - Avoid formal documentation style or academic tone
    - No bullet points or formatting - use natural speech flow
    
    Example flow:
    "In my experience... [direct answer]. This works because... [technical explanation]. For instance, when I was at... [personal example]. This approach helped us... [business impact]"

    Remember: You're having a conversation, not writing a report. Make it engaging while showcasing your expertise.
    """

    expert_prompt = template
    answer = retrieval_qa({"query": expert_prompt})
    return answer['result']


# testing
# import interview_processor

# print(generate_exp_ans_cot("What is PCA",interview_processor.retrievalQA()))