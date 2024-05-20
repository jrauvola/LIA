from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_vertexai import VertexAIEmbeddings
from langchain_google_vertexai import VertexAI
from langchain_google_community import GCSDirectoryLoader
from langchain_google_community import GCSFileLoader
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
import vertexai
from vertexai.language_models import TextGenerationModel

def initialize_rag(project_name, bucket_name, blob):
    print("Loader")
    loader = GCSFileLoader(
    project_name=project_name, 
    bucket=bucket_name,
    blob=blob
    )
    print("Loader: ", loader)
    documents = loader.load()
    print("Documents Loaded")

    embeddings = VertexAIEmbeddings(model_name = "textembedding-gecko@003")

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    docs = text_splitter.split_documents(documents)
    print("Vector DB")
    vector_db = Chroma.from_documents(docs, embeddings)

    return vector_db

def retrievalQA(retr_docs_num):
    print("Initializing Rag")
    vector_db = initialize_rag(project_name = "adsp-capstone-team-dawn", bucket_name = "lia_rag", blob = "data_science.txt")
    print("Grabbing Retriever")
    retriever = vector_db.as_retriever(
    search_type="similarity", search_kwargs={"k": retr_docs_num} #k: Number of Documents to return, defaults to 4.
    )
    print("Initialize retriever")
    vertexai.init(project="adsp-capstone-team-dawn", location="us-central1")
    print("Grab LLM")
    llm = VertexAI(
    model_name="text-bison-32k",
    max_output_tokens=256,
    temperature=0.1,
    top_p=0.8,
    top_k=40,
    verbose=True,
    )
    print("RETRIEVE")
    qa = RetrievalQA.from_chain_type(
        llm=llm, chain_type="stuff", retriever=retriever, return_source_documents=True
    )
    return qa
    
def generate_resume_questions(interview_instance):
    qa_prompt = f"""
                    Context: ```You are a recruiter interviewing a candidate for the data science role. Now you are asking the candidate first question in addition to self introduction ```
                    Prompt: *** Ask the candidate one technical interview question based on Personal Profile. Generate the question as if you are talking to the person. Make the question under 15 words.***
                    Personal Profile: '''{interview_instance.personal_profile}'''
                     """

    print("QA Retrieval")
    qa = retrievalQA(retr_docs_num=4)
    print("QA Response")
    response = qa({"query": qa_prompt})
    
    interview_instance.question_num = interview_instance.question_num + 1
    interview_instance.add_question(response["result"], question_num = interview_instance.question_num)
        
def generate_dynamic_questions(interview_instance, question_num):
    window_dict = {}
    if question_num > 1:
        for key in range(question_num-2, question_num):
            window_dict[key] = interview_instance.interview_dict[key]
    else:
        window_dict = interview_instance.interview_dict
    qa_prompt = f"""
                    Context: ```You are a nice recruiter interviewing a candidate for the data science role. Ask the candidate one follow-up interview question based on there answers recorded in Interview Conversations.```
                    Prompt: *** Ask the candidate one follow-up interview question based on there answers recorded in Interview Conversations. Generate the question as if you are talking to the person. Make sure to react to the candidate's answers. Make the question under 35 words.***
                    Interview Conversations: '''{window_dict}'''
                    Answer: """
    qa = retrievalQA(retr_docs_num=3)
    response = qa({"query": qa_prompt})
     
    question_num = question_num
    interview_instance.add_question(response["result"], question_num = question_num)