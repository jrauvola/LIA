import vertexai
from vertexai.generative_models import GenerativeModel, GenerationConfig
from langchain_core.prompts import PromptTemplate
import json

# Define expert zones
EXPERT_ZONES = {
    "text": {
        "quantifier_words_pct": [2.75, 3.42],
        "filler_nonfluency_pct": [3.30, 6.48],
        "wpsec": [3.11, 3.64],
        "upsec": [1.17, 1.38]
    },
    "audio": {
        "avgBand1": [323.9413, 394.5272],
        "unvoiced_percent": [27.39, 36.05],
        "f1STD": [262.2278, 300.5224],
        "f3meanf1": [4.5702, 4.7801],
        "intensityMean": [58.0279, 61.4552],
        "avgDurPause": [0.3365, 0.503]
    },
    "video": {
        "blink_rate": [10, 15],
        "average_smile_intensity": [30, 45],
        "average_engagement": [0.7, 0.9],
        "average_stress": [0.1, 0.3]
    }
}


class PerformanceAnalysis:
    def __init__(self):
        self.analysis_dict = {
            "overall_feedback": "",
            "video_feedback": {
                "strength": "",
                "weakness": ""
            },
            "audio_feedback": {
                "strength": "",
                "weakness": ""
            },
            "text_feedback": {
                "strength": "",
                "weakness": ""
            }
        }


def analyze_interview_performance(user_metrics, retrieval_qa):
    metrics_info = """
    TEXT FEATURES (Expert Zones):
    - quantifier_words_pct: Higher is better [2.75 - 3.42]
    - filler_nonfluency_pct: Lower is better [3.30 - 6.48]
    - wpsec: Higher is better [3.11 - 3.64]
    - upsec: Higher is better [1.17 - 1.38]

    AUDIO FEATURES (Expert Zones):
    - avgBand1: Lower is better [323.94 - 394.53]
    - unvoiced_percent: Lower is better [27.39 - 36.05]
    - f1STD: Lower is better [262.23 - 300.52]
    - f3meanf1: Higher is better [4.57 - 4.78]
    - intensityMean: Higher is better [58.03 - 61.46]
    - avgDurPause: Lower is better [0.34 - 0.50]

    VIDEO FEATURES (Expert Zones):
    - blink_rate: Aim for range [10 - 15]
    - average_smile_intensity: Aim for range [30 - 45]
    - average_engagement: Aim for range [0.7 - 0.9]
    - average_stress: Lower is better [0.1 - 0.3]
    """

    distance_analysis = "DISTANCE ANALYSIS FROM EXPERT ZONES:\n"
    for category in EXPERT_ZONES:
        distance_analysis += f"\n{category.upper()} METRICS:\n"
        for metric, zone in EXPERT_ZONES[category].items():
            if metric in user_metrics:
                value = user_metrics[metric]
                if value < zone[0]:
                    distance = zone[0] - value
                    position = "below"
                elif value > zone[1]:
                    distance = value - zone[1]
                    position = "above"
                else:
                    distance = 0
                    position = "within"
                distance_analysis += f"- {metric}: {value:.2f} ({position} expert zone [{zone[0]:.2f} - {zone[1]:.2f}])\n"

    template = f"""Context: You are an AI interview coach analyzing a candidate's mock interview performance metrics.

    METRICS REFERENCE AND EXPERT ZONES:
    {metrics_info}

    USER'S METRICS AND ANALYSIS:
    {distance_analysis}

    Provide your analysis in the following exact JSON structure:
    {{
        "overall_feedback": "A comprehensive summary of overall performance",
        "video_feedback": {{
            "strength": "The single most impressive video metric with specific values",
            "weakness": "The single video metric needing most improvement with specific values"
        }},
        "audio_feedback": {{
            "strength": "The single most impressive audio metric with specific values",
            "weakness": "The single audio metric needing most improvement with specific values"
        }},
        "text_feedback": {{
            "strength": "The single most impressive text metric with specific values",
            "weakness": "The single text metric needing most improvement with specific values"
        }}
    }}

    Requirements for each section:
    1. overall_feedback: Provide a concise summary of overall performance across all metrics
    2. For each category (video, audio, text):
       - strength: Identify the single metric where performance was best relative to expert zone
       - weakness: Identify the single metric where performance needs most improvement

    Be specific and include actual values and target ranges in your feedback.
    """

    vertexai.init(project="adsp-capstone-team-dawn", location="us-central1")
    model = GenerativeModel("gemini-1.5-flash-preview-0514")

    generation_config = GenerationConfig(
        max_output_tokens=8192,
        temperature=0.3,
        top_p=0.98
    )

    response = model.generate_content(
        template,
        generation_config=generation_config,
        stream=False
    )

    try:
        response_text = response.text.strip()
        if response_text.startswith('```json'):
            response_text = response_text[7:-3]
        analysis_dict = json.loads(response_text)

        performance_analysis = PerformanceAnalysis()
        performance_analysis.analysis_dict = analysis_dict

        return performance_analysis.analysis_dict

    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        print(f"Raw response: {response.text}")
        return PerformanceAnalysis().analysis_dict


# def test_analyze_performance():
#     class MockRetrievalQA:
#         def __call__(self, query_dict):
#             return {"result": "Mock analysis result"}
#
#     mock_metrics = {
#         "quantifier_words_pct": 3.0,
#         "filler_nonfluency_pct": 4.0,
#         "wpsec": 3.5,
#         "upsec": 1.2,
#         "blink_rate": 12,
#         "average_smile_intensity": 35,
#         "average_engagement": 0.8,
#         "average_stress": 0.2
#     }
#
#     try:
#         print("\n=== Starting Performance Analysis Test ===")
#         mock_qa = MockRetrievalQA()
#         response = analyze_interview_performance(mock_metrics, mock_qa)
#
#         print("\n--- Response Structure ---")
#         print(json.dumps(response, indent=2))
#
#         return response
#
#     except Exception as e:
#         print(f"\nError in test: {str(e)}")
#         return None
#
#
# if __name__ == "__main__":
#     print("\n=== Starting Test ===")
#     result = test_analyze_performance()
#     if result:
#         print("\n=== Test Completed Successfully ===")
#         print("Final result structure:")
#         print(json.dumps(result, indent=2))
#     else:
#         print("\n=== Test Failed ===")