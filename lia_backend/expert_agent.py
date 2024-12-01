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

    # First, try to get relevant chunks and check similarity
    context_response = retrieval_qa.retriever.vectorstore.similarity_search_with_relevance_scores(template)

    # Set similarity score threshold
    SIMILARITY_THRESHOLD = 0.65

    # Calculate average similarity if we have chunks
    use_rag = False
    if len(context_response) > 1:
        avg_similarity = sum(score for _, score in context_response) / len(context_response)
        use_rag = avg_similarity >= SIMILARITY_THRESHOLD
        print(f"Found {len(context_response)} chunks with average similarity score: {avg_similarity}")

    if use_rag:
        print("Generating expert answer using RAG knowledge base")
        answer = retrieval_qa({"query": template})
        return answer['result']

    # If similarity is too low, use Gemini directly
    print("Generating expert answer using Gemini only")
    model = VertexAI(
        model_name="gemini-1.5-pro",
        max_output_tokens=2000,
        temperature=0.1,
        top_p=0.8,
        top_k=40,
        verbose=True,
    )

    response = model.predict(template).strip('"')
    return response

# testing
# import interview_processor

# print(generate_exp_ans_cot("What is PCA",interview_processor.retrievalQA()))