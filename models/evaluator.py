from openai import OpenAI

client = OpenAI()


def evaluate_answer(answer, question):

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

    answer = answer.lower()

    required = keywords.get(question, [])

    matched = 0

    for word in required:
        if word in answer:
            matched += 1

    if len(required) == 0:
        return 0

    return round((matched / len(required)) * 10)


def get_feedback(percentage):

    if percentage >= 80:
        return {
            "performance": "Excellent 🔥",
            "strengths": [
                "Strong technical understanding",
                "Good knowledge of basic concepts",
                "Answers are relevant"
            ],
            "weaknesses": [
                "Try to give more real-world examples"
            ],
            "suggestions": [
                "Practice explaining concepts with examples",
                "Practice technical interview questions regularly"
            ]
        }

    elif percentage >= 50:
        return {
            "performance": "Good 👍",
            "strengths": [
                "Basic concepts are understood",
                "Most answers are relevant"
            ],
            "weaknesses": [
                "Some concepts need more clarity"
            ],
            "suggestions": [
                "Study weak concepts again",
                "Practice more technical questions"
            ]
        }

    else:
        return {
            "performance": "Needs Improvement 💪",
            "strengths": [
                "You attempted the interview"
            ],
            "weaknesses": [
                "Basic technical concepts need improvement"
            ],
            "suggestions": [
                "Revise fundamental concepts",
                "Practice more interview questions"
            ]
        }


# =========================
# REAL AI EVALUATION
# =========================

def ai_evaluate_answer(question, answer):

    prompt = f"""
You are an expert technical interviewer.

Evaluate the student's answer.

Question:
{question}

Student Answer:
{answer}

Give a concise evaluation.

Use this format:

Score: X/10
Technical Knowledge: X/10
Relevance: X/10
Clarity: X/10

Feedback:
Write 2-3 sentences.

Improvement:
Write 1 practical suggestion.
"""

    response = client.responses.create(
        model="gpt-5.6-luna",
        input=prompt
    )

    return response.output_text