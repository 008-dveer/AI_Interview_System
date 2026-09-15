import os
import json
import re
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


def get_grok_config():
    """
    Configures and returns the OpenAI client, model name, and base URL for Grok / Groq.
    Supports:
    - xAI Grok (default: base_url="https://api.x.ai/v1", model="grok-2-latest")
    - Groq Cloud (keys starting with 'gsk_', base_url="https://api.groq.com/openai/v1", model="llama-3.3-70b-versatile")
    """
    api_key = (
        os.getenv("GROK_API_KEY")
        or os.getenv("XAI_API_KEY")
        or os.getenv("GROQ_API_KEY")
    )

    if not api_key or api_key.strip() == "" or "YOUR_GROK_API_KEY" in api_key:
        return None, None, None

    api_key = api_key.strip()
    custom_base_url = os.getenv("GROK_BASE_URL")
    custom_model = os.getenv("GROK_MODEL")

    # If it's a Groq Cloud key (starts with 'gsk_')
    if api_key.startswith("gsk_") or (custom_base_url and "groq.com" in custom_base_url):
        base_url = custom_base_url or "https://api.groq.com/openai/v1"
        model = custom_model or "openai/gpt-oss-120b"
    else:
        # Default to xAI Grok
        base_url = custom_base_url or "https://api.x.ai/v1"
        model = custom_model or "grok-2-latest"

    try:
        client = OpenAI(api_key=api_key, base_url=base_url)
        return client, model, base_url
    except Exception as e:
        print(f"Warning: Failed to initialize Grok client: {e}")
        return None, None, None


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
    Fallback rule-based keyword evaluation if API key is not provided or unavailable.
    """
    keywords = {
        "What is Object-Oriented Programming?":
            ["class", "object", "inheritance", "polymorphism"],

        "What is inheritance in OOP?":
            ["class", "inherit", "parent", "child"],

        "What is polymorphism?":
            ["many", "form", "overloading", "overriding"],

        "What is encapsulation?":
            ["data", "method", "class", "private"],

        "What is a database?":
            ["data", "store", "table", "database"]
    }

    answer_lower = answer.lower()
    required = keywords.get(question, [])

    if len(required) == 0:
        return 5, "Answer recorded."

    matched = sum(1 for word in required if word in answer_lower)
    score = round((matched / len(required)) * 10)
    feedback = f"Matched {matched} of {len(required)} key concepts."
    return score, feedback


def evaluate_answer(answer, question):
    """
    Evaluates candidate answer using Grok AI, with fallback to keyword matching.
    Returns: (score: int, feedback: str)
    """
    client, model, _ = get_grok_config()

    if client:
        try:
            prompt = f"""You are an experienced technical interviewer.
Evaluate the candidate's answer to the following technical interview question.

Question: {question}
Candidate Answer: {answer}

Provide:
1. A score from 0 to 10 (10 being an accurate, clear, and comprehensive explanation; 0 being blank or completely incorrect).
2. A concise 1-2 sentence feedback highlighting technical accuracy or what needs improvement.

Return your response strictly as valid JSON matching this schema:
{{
  "score": <integer from 0 to 10>,
  "feedback": "<concise feedback string>"
}}
"""
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert technical interviewer. Return your response strictly as valid JSON with keys 'score' and 'feedback'."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2
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


def get_feedback(percentage, interview_history=None):
    """
    Generates structured overall feedback.
    Uses Grok AI if available and history is provided, else falls back to default brackets.
    """
    client, model, _ = get_grok_config()

    if client and interview_history:
        try:
            prompt = f"""You are a senior technical hiring manager reviewing an entire technical interview.

Overall Score Percentage: {percentage}%
Detailed Interview Log:
{json.dumps(interview_history, indent=2)}

Provide an honest, constructive summary of the candidate's performance.
Return strictly a valid JSON object in this exact schema:
{{
  "performance": "<Short summary with an emoji, e.g., 'Strong Performance 🚀'>",
  "strengths": ["<strength 1>", "<strength 2>", "<strength 3>"],
  "weaknesses": ["<weakness 1>", "<weakness 2>"],
  "suggestions": ["<suggestion 1>", "<suggestion 2>"]
}}
"""
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a technical hiring manager. Return your response strictly as valid JSON."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
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
                "Strong technical understanding",
                "Good knowledge of core concepts",
                "Answers are relevant and structured"
            ],
            "weaknesses": [
                "Try to incorporate more real-world examples and edge cases"
            ],
            "suggestions": [
                "Practice explaining system design and trade-offs",
                "Maintain consistent technical depth"
            ]
        }
    elif percentage >= 50:
        return {
            "performance": "Good 👍",
            "strengths": [
                "Basic concepts are understood",
                "Most answers are relevant to the questions"
            ],
            "weaknesses": [
                "Some explanations lack depth or technical precision"
            ],
            "suggestions": [
                "Revise core definitions and practical implementations",
                "Practice answering under timed conditions"
            ]
        }
    else:
        return {
            "performance": "Needs Improvement 💪",
            "strengths": [
                "Showed willingness to attempt the questions"
            ],
            "weaknesses": [
                "Core fundamentals need significant strengthening",
                "Answers lacked key technical terms"
            ],
            "suggestions": [
                "Review foundational OOP and computer science concepts",
                "Practice writing out explanations before speaking or submitting"
            ]
        }