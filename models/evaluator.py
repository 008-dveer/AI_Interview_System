import os
import json
import re
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# Cached client and config singleton
_CACHED_CLIENT = None
_CACHED_MODEL = None
_CACHED_BASE_URL = None
_CLIENT_INITIALIZED = False


def get_grok_config():
    """
    Returns a cached singleton OpenAI client, model name, and base URL for Grok/Groq.
    Auto-detects:
    - Groq Cloud (keys starting with 'gsk_', base_url="https://api.groq.com/openai/v1", model="openai/gpt-oss-120b")
    - xAI Grok (default: base_url="https://api.x.ai/v1", model="grok-2-latest")
    """
    global _CACHED_CLIENT, _CACHED_MODEL, _CACHED_BASE_URL, _CLIENT_INITIALIZED

    if _CLIENT_INITIALIZED:
        return _CACHED_CLIENT, _CACHED_MODEL, _CACHED_BASE_URL

    api_key = (
        os.getenv("GROK_API_KEY")
        or os.getenv("XAI_API_KEY")
        or os.getenv("GROQ_API_KEY")
    )

    if not api_key or api_key.strip() == "" or "YOUR_GROK_API_KEY" in api_key:
        _CLIENT_INITIALIZED = True
        return None, None, None

    api_key = api_key.strip()
    custom_base_url = os.getenv("GROK_BASE_URL")
    custom_model = os.getenv("GROK_MODEL")

    if api_key.startswith("gsk_") or (custom_base_url and "groq.com" in custom_base_url):
        base_url = custom_base_url or "https://api.groq.com/openai/v1"
        model = custom_model or "openai/gpt-oss-120b"
    else:
        base_url = custom_base_url or "https://api.x.ai/v1"
        model = custom_model or "grok-2-latest"

    try:
        _CACHED_CLIENT = OpenAI(api_key=api_key, base_url=base_url, timeout=20.0)
        _CACHED_MODEL = model
        _CACHED_BASE_URL = base_url
    except Exception as e:
        print(f"Warning: Failed to initialize Grok/Groq client: {e}")
        _CACHED_CLIENT = None

    _CLIENT_INITIALIZED = True
    return _CACHED_CLIENT, _CACHED_MODEL, _CACHED_BASE_URL


def extract_json(raw_text):
    """
    Safely extract JSON from model response even if surrounded by markdown code fences.
    """
    text = raw_text.strip()
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        text = match.group(0)
    return json.loads(text)


def keyword_evaluate(answer, question):
    """
    Fallback rule-based evaluation if API is unavailable.
    """
    answer_lower = answer.lower()
    words = answer_lower.split()

    if len(words) < 3:
        return 2, "Answer is too brief to evaluate technical depth."

    # Heuristic scoring based on length and common technical structure
    word_count = len(words)
    if word_count > 30:
        score = 8
        feedback = "Detailed explanation provided with good technical context."
    elif word_count > 15:
        score = 6
        feedback = "Relevant answer, but could be elaborated with real-world examples."
    else:
        score = 4
        feedback = "Basic response provided; expand with more technical definitions."

    return score, feedback


def evaluate_answer(answer, question, topic="Technical"):
    """
    Evaluates candidate answer using Grok AI, with fallback.
    Returns: (score: int, feedback: str)
    """
    answer_clean = answer.strip() if answer else ""
    if len(answer_clean.split()) < 3:
        return 1, "The answer was blank or too brief to demonstrate technical competency."

    client, model, _ = get_grok_config()

    if client:
        try:
            prompt = f"""You are a senior technical interviewer conducting a {topic} interview.
Evaluate the candidate's answer to the question below.

Question: {question}
Candidate Answer: {answer_clean}

Criteria:
- Technical accuracy
- Completeness and depth
- Clarity of explanation

Return strictly a valid JSON object matching this schema:
{{
  "score": <integer from 0 to 10>,
  "feedback": "<concise 1-2 sentence feedback explaining what was good or what needs improvement>"
}}
"""
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": f"You are an expert {topic} interviewer. Respond strictly with valid JSON."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=250
            )

            raw = response.choices[0].message.content
            data = extract_json(raw)
            score = int(data.get("score", 5))
            score = max(0, min(10, score))
            feedback = data.get("feedback", "Answer evaluated.")
            return score, feedback

        except Exception as e:
            print(f"Grok evaluation failed ({e}). Falling back to keyword evaluator.")

    return keyword_evaluate(answer, question)


def get_feedback(percentage, interview_history=None, topic="Technical"):
    """
    Generates structured overall feedback.
    Uses AI if available and history is provided, else falls back to default brackets.
    """
    client, model, _ = get_grok_config()

    if client and interview_history:
        try:
            prompt = f"""You are a senior hiring manager reviewing an entire candidate interview for a {topic} role.

Overall Score Percentage: {percentage}%
Detailed Question & Answer Log:
{json.dumps(interview_history, indent=2)}

Provide an honest, constructive summary of the candidate's performance.
Return strictly a valid JSON object in this exact schema:
{{
  "performance": "<Short summary with an emoji, e.g., 'Strong Performance 🚀'>",
  "strengths": ["<strength 1>", "<strength 2>", "<strength 3>"],
  "weaknesses": ["<area to improve 1>", "<area to improve 2>"],
  "suggestions": ["<actionable recommendation 1>", "<actionable recommendation 2>"]
}}
"""
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": f"You are a technical hiring manager specializing in {topic}. Return strictly valid JSON."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=400
            )

            raw = response.choices[0].message.content
            data = extract_json(raw)
            return {
                "performance": data.get("performance", "Interview Completed 👍"),
                "strengths": data.get("strengths", ["Attempted all technical questions"]),
                "weaknesses": data.get("weaknesses", ["Review missed conceptual points"]),
                "suggestions": data.get("suggestions", ["Keep practicing technical problems"])
            }

        except Exception as e:
            print(f"Grok feedback generation failed ({e}). Using default feedback.")

    # Fallback rule-based feedback
    if percentage >= 80:
        return {
            "performance": "Excellent 🔥",
            "strengths": [
                f"Strong understanding of {topic} principles",
                "Good technical articulation and clarity",
                "Demonstrated relevant conceptual knowledge"
            ],
            "weaknesses": [
                "Incorporate more real-world system design and edge-case handling"
            ],
            "suggestions": [
                "Practice explaining architectural trade-offs",
                "Continue maintaining consistent technical depth"
            ]
        }
    elif percentage >= 50:
        return {
            "performance": "Good 👍",
            "strengths": [
                f"Basic {topic} fundamentals are understood",
                "Answers are relevant to the questions asked"
            ],
            "weaknesses": [
                "Some explanations lacked technical depth or specific terminology"
            ],
            "suggestions": [
                "Revise core definitions and practical implementations",
                "Practice answering technical questions under timed conditions"
            ]
        }
    else:
        return {
            "performance": "Needs Improvement 💪",
            "strengths": [
                "Showed willingness to engage with challenging interview questions"
            ],
            "weaknesses": [
                f"Core {topic} concepts require further study and revision",
                "Answers were too brief or missed key mechanisms"
            ],
            "suggestions": [
                f"Review fundamental {topic} documentation and tutorials",
                "Practice mock interviews focusing on structuring explanations clearly"
            ]
        }