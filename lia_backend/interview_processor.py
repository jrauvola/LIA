# test
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_vertexai import VertexAIEmbeddings
from langchain_google_vertexai import VertexAI
from langchain_google_community import GCSDirectoryLoader
from langchain_google_community import GCSFileLoader
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
import vertexai
from vertexai.language_models import TextGenerationModel
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field


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

    embeddings = VertexAIEmbeddings(model_name="textembedding-gecko@003")

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    docs = text_splitter.split_documents(documents)
    print("Vector DB")
    vector_db = Chroma.from_documents(docs, embeddings)

    return vector_db


def retrievalQA():
    print("Initializing Rag")
    vector_db = initialize_rag(project_name="adsp-capstone-team-dawn", bucket_name="lia_rag", blob="data_science.txt")
    print("Grabbing Retriever")
    retriever = vector_db.as_retriever(
        search_type="similarity", 
        search_kwargs={"k": 4}  # k: Number of Documents to return, defaults to 4.
    )
    print("Initialize retriever")
    vertexai.init(project="adsp-capstone-team-dawn", location="us-central1")
    print("Grab LLM")
    llm = VertexAI(
        model_name="gemini-pro",
        max_output_tokens=2000,
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

# Q2 and Q3
def generate_resume_questions(interview_instance):
    class ResumeQuestion(BaseModel):
        question: str = Field(description="interview question")

    query = f"""
                Context: ```You are a recruiter interviewing a candidate for the data science role. Now you are asking the candidate first question in addition to self introduction ```
                Prompt: *** Ask the candidate one technical interview question based on Personal Profile. Be conversational and specific. Make the question under 30 words.***
                Personal Profile: '''{interview_instance.personal_profile}'''
                """
    model = VertexAI(
        model_name="gemini-pro",
        max_output_tokens=2000,
        temperature=0.1,
        top_p=0.8,
        top_k=40,
        verbose=True,
    )
    parser = JsonOutputParser(pydantic_object=ResumeQuestion)

    prompt = PromptTemplate(
        template="Answer the user query.\n{format_instructions}\n{query}\n",
        input_variables=["query"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )
    chain = prompt | model | parser
    question = chain.invoke({"query": query})

    interview_instance.add_question(question["question"], question_num=interview_instance.question_num + 1)


# Q4 and Q5
def generate_dynamic_questions(qa, interview_instance):
    window_dict = {}
    question_num = interview_instance.question_num
    if question_num > 1:
        for key in range(question_num - 2, question_num):
            window_dict[key] = interview_instance.interview_dict[key]
    else:
        window_dict = interview_instance.interview_dict
    qa_prompt = f"""
                    Context: ```You are a nice recruiter interviewing a candidate for the data science role. Ask the candidate one follow-up interview question based on there answers recorded in Interview Conversations.```
                    Prompt: *** Ask the candidate one follow-up interview question based on there answers recorded in Interview Conversations. Generate only the question to be asked, as if you are talking to the person. Make sure to react to the candidate's answers. Make the question under 35 words.***
                    Interview Conversations: '''{window_dict}'''
                    Answer: """

    retries = 0
    fallback_question = "Can you elaborate on your previous answer and provide more details?"
    max_retries = 2

    while retries < max_retries:
        response = qa({"query": qa_prompt})
        question = response["result"]

        if question and not question.lower().startswith("i'm sorry") and len(question.split()) < 40:
            # question_num = question_num
            interview_instance.add_question(response["result"], question_num=question_num + 1)
        else:
            interview_instance.add_question(fallback_question, question_num=question_num + 1)


    print("Question Generated")