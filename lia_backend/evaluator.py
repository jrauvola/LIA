import base64
import vertexai
from vertexai.generative_models import GenerativeModel, GenerationConfig
from langchain_core.prompts import PromptTemplate
import json


class evaluation_class:
    def __init__(self):
        self.evaluation_dict = {
            0: {
                "Relevance to the Question": {
                    "Score": 0,
                    "Justification": ""
                },
                "Technical Correctness": {
                    "Score": 0,
                    "Justification": ""
                },
                "Completeness of the Answer": {
                    "Score": 0,
                    "Justification": ""
                },
                "Anecdotal Element": {
                    "Score": 0,
                    "Justification": ""
                },
                "Communication Clarity": {
                    "Score": 0,
                    "Justification": ""
                },
                "Problem Solving Approach": {
                    "Score": 0,
                    "Justification": ""
                },
                "Handling Ambiguity": {
                    "Score": 0,
                    "Justification": ""
                }
            }
        }


def eval_input(interview_instance, question_num):
    question = interview_instance.interview_dict[question_num]["question"]
    answer = interview_instance.interview_dict[question_num]["answer"]

    template = """
   You are an AI designed to evaluate answers to data science interview questions. You will be provided with an interview question and a candidate's answer. Your task is to score the answer using the following rubric, providing a justification for each score.

   Question: {question}
   Answer: {answer}

   Return the evaluation in this exact JSON structure:
   {{
       "Relevance to the Question": {{"Score": <int>, "Justification": <str>}},
       "Technical Correctness": {{"Score": <int>, "Justification": <str>}},
       "Completeness of the Answer": {{"Score": <int>, "Justification": <str>}},
       "Anecdotal Element": {{"Score": <int>, "Justification": <str>}},
       "Communication Clarity": {{"Score": <int>, "Justification": <str>}},
       "Problem Solving Approach": {{"Score": <int>, "Justification": <str>}},
       "Handling Ambiguity": {{"Score": <int>, "Justification": <str>}}
   }}

    Scoring Guidelines:
    1. Relevance to the Question (0-3):
        * 0 - Completely off-topic
        * 1 - Mostly irrelevant
        * 2 - Partially relevant, some tangential discussion
        * 3 - Directly addresses the question and remains focused

    2. Technical Correctness (0-3):
        * 0 - Significant factual errors
        * 1 - Minor inaccuracies or misunderstandings
        * 2 - Mostly correct, with some minor omissions
        * 3 - Completely accurate and demonstrates strong technical understanding

    3. Completeness of the Answer (0-3):
        * 0 - Incomplete and missing key aspects
        * 1 - Addresses some aspects but lacks depth
        * 2 - Addresses most aspects but could be more comprehensive
        * 3 - Thoroughly addresses all aspects, anticipating potential follow-up questions

    4. Anecdotal Element (0-3):
        * 0 - No relevant examples
        * 1 - Weak or irrelevant example(s)
        * 2 - One or two relevant examples
        * 3 - Multiple compelling examples that clearly illustrate the candidate's experience

    5. Communication Clarity (0-3):
        * 0 - Unclear and difficult to understand
        * 1 - Mostly unclear, some clear parts
        * 2 - Mostly clear, some unclear parts
        * 3 - Clear, concise, and easy to understand

    6. Problem Solving Approach (0-3):
        * 0 - No discernible approach
        * 1 - Illogical or incomplete approach
        * 2 - Mostly logical approach, some gaps
        * 3 - Systematic and logical approach

    7. Handling Ambiguity (0-3):
        * 0 - Unable to handle ambiguity
        * 1 - Attempts to handle ambiguity but struggles
        * 2 - Mostly handles ambiguity effectively
        * 3 - Effectively handles ambiguity, making reasonable assumptions or asking clarifying questions

    Provide your evaluation in the exact JSON format specified above.
   """

    prompt = PromptTemplate(template=template, input_variables=["question", "answer"])
    eval_prompt = prompt.format(question=question, answer=answer)

    vertexai.init(project="adsp-capstone-team-dawn", location="us-central1")
    model = GenerativeModel("gemini-1.5-flash-preview-0514")


    generation_config = GenerationConfig(
        max_output_tokens=8192,
        temperature=0.3,
        top_p=0.98
    )

    response = model.generate_content(
        eval_prompt,
        generation_config=generation_config,
        stream=False
    )

    try:
        # Clean the response text to ensure valid JSON
        response_text = response.text.strip()
        if response_text.startswith('```json'):
            response_text = response_text[7:-3]
        return json.loads(response_text)

    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        print(f"Raw response: {response.text}")
        # Return a default structured response if parsing fails
        return {
            category: {
                "Score": 0,
                "Justification": "Error processing evaluation"
            } for category in [
                "Relevance to the Question",
                "Technical Correctness",
                "Completeness of the Answer",
                "Anecdotal Element",
                "Communication Clarity",
                "Problem Solving Approach",
                "Handling Ambiguity"
            ]
        }


def test_eval_input():
    class MockInterview:
        def __init__(self):
            self.interview_dict = {
                0: {
                    "question": "What is PCA?",
                    "answer": "PCA is a dimensionality reduction technique that transforms high-dimensional data into lower dimensions while preserving maximum variance."
                }
            }

    mock_interview = MockInterview()

    try:
        print("\n=== Starting Evaluation Test ===")
        print("\nTest Question:", mock_interview.interview_dict[0]["question"])
        print("Test Answer:", mock_interview.interview_dict[0]["answer"])

        print("\n--- Calling eval_input ---")
        response = eval_input(mock_interview, 0)

        print("\n--- Response from Model ---")
        print("Response type:", type(response))
        print("Response structure:")
        print(json.dumps(response, indent=2))

        # Validate expected keys
        expected_keys = [
            "Relevance to the Question",
            "Technical Correctness",
            "Completeness of the Answer",
            "Anecdotal Element",
            "Communication Clarity",
            "Problem Solving Approach",
            "Handling Ambiguity"
        ]

        print("\n--- Validating Structure ---")
        missing_keys = [key for key in expected_keys if key not in response]
        if missing_keys:
            print("Warning: Missing expected keys:", missing_keys)
        else:
            print("All expected keys present")

        return response

    except Exception as e:
        print("\n!!! Unexpected Error !!!")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        import traceback
        print("\nFull traceback:")
        print(traceback.format_exc())
        return None

if __name__ == "__main__":
    print("\n=== Starting Test ===")
    vertexai.init(project="adsp-capstone-team-dawn", location="us-central1")
    result = test_eval_input()
    if result:
        print("\n=== Test Completed Successfully ===")
        print("Final result structure:")
        print(json.dumps(result, indent=2))
    else:
        print("\n=== Test Failed ===")