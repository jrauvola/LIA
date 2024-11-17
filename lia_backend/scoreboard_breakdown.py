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


def analyze_interview_performance(user_metrics, retrieval_qa):
    # Create a formatted string of expert zones with descriptions
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

    # Calculate distance from expert zones for each metric
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

    Task: Analyze the candidate's performance following these steps:

    1. Overall Assessment:
    - Evaluate how many metrics fall within, above, or below their expert zones
    - Assess the magnitude of deviation from expert zones where applicable

    2. Detailed Analysis:
    - Identify the TWO metrics where the candidate performed best (closest to or within expert zone, considering whether higher/lower is better)
    - Identify the TWO metrics where the candidate needs the most improvement (furthest from expert zone)
    - Group observations by text, audio, and video categories

    3. Provide a comprehensive summary that:
    - Starts with an overall assessment of performance relative to expert zones
    - Details specific strengths and areas for improvement with exact values and target ranges
    - Groups insights by feature category (text, audio, video)
    - Maintains a constructive and encouraging tone
    - Provides specific, actionable recommendations for improving the metrics furthest from expert zones

    Format your response in clear sections with specific metrics, values, and expert zones mentioned.
    """

    analysis_prompt = template.format(metrics=user_metrics)

    analysis = retrieval_qa({"query": analysis_prompt})

    return analysis['result']

