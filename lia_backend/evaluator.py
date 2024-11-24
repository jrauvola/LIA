import base64
import vertexai
from vertexai.generative_models import GenerativeModel # to call Gemini
from langchain_core.prompts import PromptTemplate


def eval_input(interview_instance, question_num):
    question = interview_instance.interview_dict[question_num]["question"]
    answer =  interview_instance.interview_dict[question_num]["answer"]

    template = """
    You are an AI designed to evaluate answers to data science interview questions.  You will be provided with an interview question and a candidate's answer.  Your task is to score the answer using the following rubric, providing a justification for each score.  Finally, sum the scores to produce a total score out of 21.
    Question: {question}
    Answer: {answer}
    **Scoring Rubric:**

    1. **Relevance to the Question (0-3):** How well the answer addresses the specific question asked. The response should be on-topic, focused, and tailored to the question's intent. Points should be deducted if the answer goes off on tangents or includes information not directly related to the question.
        * 0 - Completely off-topic
        * 1 - Mostly irrelevant
        * 2 - Partially relevant, some tangential discussion
        * 3 - Directly addresses the question and remains focused

    2. **Technical Correctness (0-3):**  The accuracy of the technical content. The response should demonstrate a solid understanding of data science concepts, methodologies, or tools mentioned. Look for errors in logic, incorrect explanations, or inaccuracies in technical terminology.
        * 0 - Significant factual errors
        * 1 - Minor inaccuracies or misunderstandings
        * 2 - Mostly correct, with some minor omissions
        * 3 - Completely accurate and demonstrates strong technical understanding

    3. **Completeness of the Answer (0-3):** How thorough the answer is. A strong response should cover all relevant aspects of the question, including any logical steps, methods, or nuances that demonstrate comprehensive knowledge. A complete answer often anticipates follow-up questions or provides context for complex concepts.
        * 0 - Incomplete and missing key aspects
        * 1 - Addresses some aspects but lacks depth
        * 2 - Addresses most aspects but could be more comprehensive
        * 3 - Thoroughly addresses all aspects, anticipating potential follow-up questions

    4. **Anecdotal Element (0-3):** Whether the answer includes relevant examples, anecdotes, or real-world applications that enhance the response. Strong anecdotes illustrate practical experience, demonstrate the candidate's hands-on knowledge, and make the answer more engaging. Examples should be directly related to the question, showcasing the candidate’s expertise.
        * 0 - No relevant examples
        * 1 - Weak or irrelevant example(s)
        * 2 - One or two relevant examples
        * 3 - Multiple compelling examples that clearly illustrate the candidate's experience

    5. **Communication Clarity (0-3):** How clearly and concisely the candidate expresses their ideas.  A clear answer is easy to understand, avoids jargon when possible, and uses precise language.
        * 0 - Unclear and difficult to understand
        * 1 - Mostly unclear, some clear parts
        * 2 - Mostly clear, some unclear parts
        * 3 - Clear, concise, and easy to understand

    6. **Problem-Solving Approach (0-3):** How systematically and logically the candidate approaches the problem.  A good approach breaks down the problem into smaller parts, considers different solutions, and justifies the chosen approach.
        * 0 - No discernible approach
        * 1 - Illogical or incomplete approach
        * 2 - Mostly logical approach, some gaps
        * 3 - Systematic and logical approach

    7. **Handling Ambiguity (0-3):** The candidate's ability to deal with incomplete or unclear information.  This assesses whether the candidate identifies missing information, makes reasonable assumptions, or asks clarifying questions.
        * 0 - Unable to handle ambiguity
        * 1 - Attempts to handle ambiguity but struggles
        * 2 - Mostly handles ambiguity effectively
        * 3 - Effectively handles ambiguity, making reasonable assumptions or asking clarifying questions

    """
    prompt = PromptTemplate(
        template=template,
        input_variables=["question", "answer"],
    )

    eval_prompt = prompt.format(question=question, answer=answer)

    vertexai.init(project="adsp-capstone-team-dawn", location="us-central1")
    model = GenerativeModel("gemini-1.5-flash-preview-0514")

    generation_config = {
        "max_output_tokens": 8192,
        "temperature": 0.3,
        "top_p": 0.98,
    }

    responses = model.generate_content(
        eval_prompt,
        generation_config=generation_config)
    return responses.text
