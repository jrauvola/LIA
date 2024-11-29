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
def generate_resume_questions(qa, interview_instance):
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


def generate_job_specific_question(interview_instance):
    class JobSpecificQuestion(BaseModel):
        question: str = Field(description="interview question")

    query = f"""
                Context: ```You are a recruiter interviewing a candidate for a {interview_instance.personal_profile['role']} position in the {interview_instance.personal_profile['industry']} industry. This role has the following description: {interview_instance.personal_profile['job_description']}
                The candidate has {interview_instance.personal_profile['experience']} years of experience.
                You need to assess if they have the right qualifications and mindset for this specific role and industry.

                Their profile information is:
                {interview_instance.personal_profile['personal_profile']}```

                Prompt: *** Generate one technical question that:
                1. Focuses on how their skills would apply to real challenges in this specific industry and role
                2. Tests their understanding of industry-specific requirements
                3. Evaluates their readiness for this particular role's responsibilities 

                The question should be:
                - Conversational and under 30 words
                - Forward-looking (about future scenarios, not past experiences)

                IMPORTANT: Return ONLY a JSON object with a single "question" field containing your generated question.
                Example format: {{"question": "Your question here..."}}
                Do not include any other text or explanations.***
                """

    model = VertexAI(
        model_name="gemini-pro",
        max_output_tokens=2000,
        temperature=0.1,
        top_p=0.8,
        top_k=40,
        verbose=True,
    )
    parser = JsonOutputParser(pydantic_object=JobSpecificQuestion)

    prompt = PromptTemplate(
        template="Answer the user query.\n{format_instructions}\n{query}\n",
        input_variables=["query"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    chain = prompt | model | parser
    question = chain.invoke({"query": query})
    clean_question = question["question"].strip('"')

    interview_instance.add_question(clean_question, question_num=interview_instance.question_num + 1)

def generate_super_technical_question(qa, interview_instance):
    class TechnicalQuestion(BaseModel):
        question: str = Field(description="technical interview question")

    window_dict = {}
    question_num = interview_instance.question_num
    window_dict[question_num - 1] = {
        "question": interview_instance.interview_dict[question_num - 1]["question"],
        "answer": interview_instance.interview_dict[question_num - 1]["answer"]
    }

    context_prompt = f"""
        Based on this interview conversation, their technical background, and the target role:
        Previous Answer: '''{window_dict}'''
        Profile: '''{interview_instance.personal_profile}'''

        Identify advanced technical concepts that bridge their background with {interview_instance.personal_profile['industry']} industry needs and the demands of the job listed here: {interview_instance.personal_profile['job_description']}.
    """

    context_response = qa.retriever.vectorstore.similarity_search_with_relevance_scores(context_prompt)

    print("DEBUG: Type of context_response:", type(context_response))
    print("DEBUG: Example of first response with score:", context_response[0] if context_response else "No results")

    SIMILARITY_THRESHOLD = 0.65

    use_rag = False
    if len(context_response) > 1:
        avg_similarity = sum(score for _, score in context_response) / len(context_response)
        use_rag = avg_similarity >= SIMILARITY_THRESHOLD
        print(f"Found {len(context_response)} chunks with average similarity score: {avg_similarity}")

    model = VertexAI(
        model_name="gemini-pro",
        max_output_tokens=2000,
        temperature=0.1,
        top_p=0.8,
        top_k=40,
        verbose=True,
    )
    parser = JsonOutputParser(pydantic_object=TechnicalQuestion)

    if use_rag:
        print("Using RAG Knowledge Base")
        question_prompt = f"""
            Context: ```You are a technical interviewer for a {interview_instance.personal_profile['role']} position in the {interview_instance.personal_profile['industry']} industry.
            The job description is: {interview_instance.personal_profile['job_description']}
            The candidate has experience in: {interview_instance.personal_profile['personal_profile']}
            Their most recent answer was: {window_dict}```

            Generate one in-depth technical question that:
            1. Tests how they would apply their existing technical skills to {interview_instance.personal_profile['industry']}-specific challenges
            2. Focuses on system architecture, ML pipeline design, or model deployment in an {interview_instance.personal_profile['industry']} context
            3. Allows them to demonstrate both technical knowledge and industry understanding
            4. Must be under 50 words and end with a question mark
            5. Should bridge their current expertise with {interview_instance.personal_profile['job_description']} requirements

            IMPORTANT: Return ONLY a JSON object with a single "question" field containing your generated question.
            Example format: {{"question": "Your question here..."}}
            Do not include any other text or explanations.

            The question should involve realistic technical challenges they would face in this role.
            """

        prompt = PromptTemplate(
            template="Answer the user query.\n{format_instructions}\n{query}\n",
            input_variables=["query"],
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )
        chain = prompt | model | parser
        response = chain.invoke({"query": question_prompt})
        clean_question = response["question"].strip('"')
        interview_instance.add_question(clean_question, question_num=question_num + 1)
        return

    print("Using Gemini-only approach")
    gemini_prompt = f"""
            Context: ```You are conducting the final technical portion of an interview for a {interview_instance.personal_profile['role']} position in {interview_instance.personal_profile['industry']}.
            The candidate has the following background: {interview_instance.personal_profile['personal_profile']}
            Their most recent answer was: {window_dict}```

            Generate one in-depth technical question that:
            1. Tests how they would apply their existing technical skills to {interview_instance.personal_profile['industry']}-specific challenges
            2. Focuses on system architectures, pipeline designs, workflows, and engineering strategies in the context of the job description {interview_instance.personal_profile['job_description']}
            3. Allows them to demonstrate both technical knowledge and industry understanding
            4. Must be under 50 words and end with a question mark
            5. Should bridge their current expertise with {interview_instance.personal_profile['role']} requirements

            IMPORTANT: Return ONLY a JSON object with a single "question" field containing your generated question.
            Example format: {{"question": "Your question here..."}}
            Do not include any other text or explanations.

            The question should probe areas like:
            - How their technical skills would solve industry-specific problems
            - Architecture decisions for {interview_instance.personal_profile['industry']} use cases
            - Scaling and deployment considerations in this industry
            - Technical tradeoffs specific to this domain
            """

    prompt = PromptTemplate(
        template="Answer the user query.\n{format_instructions}\n{query}\n",
        input_variables=["query"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )
    chain = prompt | model | parser
    response = chain.invoke({"query": gemini_prompt})
    clean_question = response["question"].strip('"')
    interview_instance.add_question(clean_question, question_num=question_num + 1)
    print("Generated super technical question using Gemini only")

# Q5 only
def generate_dynamic_questions(qa, interview_instance):
    class DynamicQuestion(BaseModel):
        question: str = Field(description="follow-up interview question")

    parser = JsonOutputParser(pydantic_object=DynamicQuestion)

    # Define model at the start so it's available for both paths
    model = VertexAI(
        model_name="gemini-pro",
        max_output_tokens=2000,
        temperature=0.1,
        top_p=0.8,
        top_k=40,
        verbose=True,
    )

    window_dict = {}
    question_num = interview_instance.question_num
    if question_num > 1:
        for key in range(question_num - 3, question_num):
            window_dict[key] = {
                "question": interview_instance.interview_dict[key]["question"],
                "answer": interview_instance.interview_dict[key]["answer"]
            }
    else:
        # For the first question, just get Q0's info
        window_dict = {
            0: {
                "question": interview_instance.interview_dict[0]["question"],
                "answer": interview_instance.interview_dict[0]["answer"]
            }
        }

    # First, try to get relevant chunks from knowledge base
    context_prompt = f"""
        Based on this interview conversation, what technical concepts should be explored:
        '''{window_dict}'''
    """

    # Get the response with source documents and scores
    context_response = qa.retriever.vectorstore.similarity_search_with_relevance_scores(context_prompt)

    print("DEBUG: Type of context_response:", type(context_response))
    print("DEBUG: Example of first response with score:", context_response[0] if context_response else "No results")

    # Set similarity score threshold
    SIMILARITY_THRESHOLD = 0.65  # Adjust this value based on testing

    # Calculate average similarity if we have chunks
    use_rag = False
    if len(context_response) > 1:
        avg_similarity = sum(score for _, score in context_response) / len(context_response)
        use_rag = avg_similarity >= SIMILARITY_THRESHOLD
        print("Using RAG Knowledge Base")
        print(f"Found {len(context_response)} chunks with average similarity score: {avg_similarity}")

    if use_rag:
        qa_prompt = f"""
                Context: ```You are a nice recruiter interviewing a candidate for the data science role. Review their answers recorded in Interview Conversations to formulate your next question.```

                Based on these Interview Conversations: '''{window_dict}'''

                Generate one follow-up interview question that:
                1. Builds directly on the candidate's previous answers
                2. Is under 35 words
                3. Is phrased directly as a question without any preamble

                IMPORTANT: Return ONLY a JSON object with a single "question" field containing your generated question.
                Example format: {{"question": "Your question here..."}}
                Do not include any other text or explanations.
                """

        prompt = PromptTemplate(
            template="Answer the user query.\n{format_instructions}\n{query}\n",
            input_variables=["query"],
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )

        retries = 0
        max_retries = 2

        while retries < max_retries:
            try:
                chain = prompt | model | parser
                response = chain.invoke({"query": qa_prompt})
                clean_question = response["question"].strip('"')

                if len(clean_question.split()) < 40:
                    interview_instance.add_question(clean_question, question_num=question_num + 1)
                    print("Generated question using RAG knowledge base")
                    return

            except Exception as e:
                print(f"RAG attempt {retries} failed: {e}")

            retries += 1

    # Gemini fallback with same structured approach
    print("Using Gemini-only approach")
    gemini_prompt = f"""
                Context: ```You are a nice recruiter interviewing a candidate for the data science role. Review their answers recorded in Interview Conversations to formulate your next question.```

                Based on these Interview Conversations: '''{window_dict}'''

                Generate one follow-up interview question that:
                1. Builds directly on the candidate's previous answers
                2. Is under 35 words
                3. Is phrased directly as a question without any preamble

                IMPORTANT: Return ONLY a JSON object with a single "question" field containing your generated question.
                Example format: {{"question": "Your question here..."}}
                Do not include any other text or explanations.
                """

    prompt = PromptTemplate(
        template="Answer the user query.\n{format_instructions}\n{query}\n",
        input_variables=["query"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )
    chain = prompt | model | parser
    response = chain.invoke({"query": gemini_prompt})
    clean_question = response["question"].strip('"')
    interview_instance.add_question(clean_question, question_num=question_num + 1)
    print("Generated question using Gemini only")