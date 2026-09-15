from flask import Blueprint, render_template, request, session, redirect, url_for
from models.questions import QUESTION_BANKS, questions as default_questions
from models.evaluator import evaluate_answer, get_feedback

interview_bp = Blueprint("interview", __name__)


@interview_bp.route("/start", methods=["POST"])
def start_interview():
    """
    Initializes a new interview session with the chosen topic and question count.
    """
    topic = request.form.get("topic", "OOP & Software Design")
    question_count = int(request.form.get("count", 5))

    bank = QUESTION_BANKS.get(topic, default_questions)
    selected_questions = bank[:question_count]

    session["topic"] = topic
    session["selected_questions"] = selected_questions
    session["scores"] = []
    session["history"] = []

    return redirect(url_for("interview.interview"))


@interview_bp.route("/interview", methods=["GET", "POST"])
def interview():
    topic = session.get("topic", "OOP & Software Design")
    current_questions = session.get("selected_questions")

    # If session is empty or user visited directly, load default questions
    if not current_questions:
        current_questions = QUESTION_BANKS.get(topic, default_questions)
        session["selected_questions"] = current_questions
        session["scores"] = []
        session["history"] = []

    total_questions = len(current_questions)

    if request.method == "POST":
        answer = request.form.get("answer", "").strip()
        number = int(request.form.get("number", 0))

        if number < total_questions:
            question = current_questions[number]
        else:
            question = current_questions[-1]

        # Evaluate via AI with topic context
        score, feedback_text = evaluate_answer(answer, question, topic=topic)

        scores = session.get("scores", [])
        scores.append(score)
        session["scores"] = scores

        history = session.get("history", [])
        history.append({
            "question": question,
            "answer": answer if answer else "(No answer provided)",
            "score": score,
            "feedback": feedback_text
        })
        session["history"] = history

        # Next question check
        if number + 1 < total_questions:
            return render_template(
                "interview.html",
                question=current_questions[number + 1],
                number=number + 1,
                total_questions=total_questions,
                topic=topic
            )

        # Final score calculation
        total_score = sum(scores)
        max_score = total_questions * 10
        percentage = round((total_score / max_score) * 100) if max_score > 0 else 0

        # Generate comprehensive overall AI feedback
        feedback = get_feedback(percentage, interview_history=history, topic=topic)

        return render_template(
            "result.html",
            score=total_score,
            max_score=max_score,
            percentage=percentage,
            performance=feedback["performance"],
            strengths=feedback["strengths"],
            weaknesses=feedback["weaknesses"],
            suggestions=feedback["suggestions"],
            history=history,
            topic=topic
        )

    # GET request - reset interview progress
    session["scores"] = []
    session["history"] = []

    return render_template(
        "interview.html",
        question=current_questions[0],
        number=0,
        total_questions=total_questions,
        topic=topic
    )