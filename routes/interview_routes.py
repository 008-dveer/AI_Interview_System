from flask import Blueprint, render_template, request, session
from models.questions import questions
from models.evaluator import evaluate_answer, get_feedback

interview_bp = Blueprint("interview", __name__)


@interview_bp.route("/interview", methods=["GET", "POST"])
def interview():

    if request.method == "POST":

        # Student's answer
        answer = request.form.get("answer", "").strip()

        # Current question number
        number = int(request.form.get("number", 0))

        # Current question
        question = questions[number]

        # Evaluate answer via AI (with fallback)
        score, feedback_text = evaluate_answer(answer, question)

        # Save scores to session
        scores = session.get("scores", [])
        scores.append(score)
        session["scores"] = scores

        # Save question history to session for detailed AI feedback
        history = session.get("history", [])
        history.append({
            "question": question,
            "answer": answer,
            "score": score,
            "feedback": feedback_text
        })
        session["history"] = history

        # Next question check
        if number + 1 < len(questions):
            return render_template(
                "interview.html",
                question=questions[number + 1],
                number=number + 1,
                total_questions=len(questions)
            )

        # Final score calculation
        total_score = sum(scores)
        max_score = len(questions) * 10
        percentage = round((total_score / max_score) * 100) if max_score > 0 else 0

        # Generate comprehensive overall AI feedback
        feedback = get_feedback(percentage, interview_history=history)

        # Render result page
        return render_template(
            "result.html",
            score=total_score,
            max_score=max_score,
            percentage=percentage,
            performance=feedback["performance"],
            strengths=feedback["strengths"],
            weaknesses=feedback["weaknesses"],
            suggestions=feedback["suggestions"],
            history=history
        )

    # Reset session on new interview start
    session["scores"] = []
    session["history"] = []

    return render_template(
        "interview.html",
        question=questions[0],
        number=0,
        total_questions=len(questions)
    )