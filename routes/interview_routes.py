from flask import Blueprint, render_template, request, session
from models.questions import questions
from models.evaluator import evaluate_answer, get_feedback

interview_bp = Blueprint("interview", __name__)


@interview_bp.route("/interview", methods=["GET", "POST"])
def interview():

    if request.method == "POST":

        # Student ka answer
        answer = request.form["answer"]

        # Current question number
        number = int(request.form["number"])

        # Current question
        question = questions[number]

        # Answer evaluate karo
        score = evaluate_answer(answer, question)

        # Score session mein save karo
        scores = session.get("scores", [])
        scores.append(score)
        session["scores"] = scores

        # Agar next question hai
        if number + 1 < len(questions):

            return render_template(
                "interview.html",
                question=questions[number + 1],
                number=number + 1
            )

        # Final score
        total_score = sum(scores)

        max_score = len(questions) * 10

        percentage = round(
            (total_score / max_score) * 100
        )

        # Feedback generate karo
        feedback = get_feedback(percentage)

        # Result page
        return render_template(
            "result.html",
            score=total_score,
            max_score=max_score,
            percentage=percentage,
            performance=feedback["performance"],
            strengths=feedback["strengths"],
            weaknesses=feedback["weaknesses"],
            suggestions=feedback["suggestions"]
        )

    # New interview start hone par scores reset
    session["scores"] = []

    return render_template(
        "interview.html",
        question=questions[0],
        number=0
    )