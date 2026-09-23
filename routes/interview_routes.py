import uuid
from flask import Blueprint, render_template, request, session, redirect, url_for
from models.questions import QUESTION_BANKS, questions as default_questions, get_interview_questions
from models.evaluator import evaluate_answer, get_feedback

interview_bp = Blueprint("interview", __name__)

# Server-side store for active interview sessions (keyed by UUID)
# Prevents cookie size overflow (>4KB) and browser session loss
INTERVIEW_SESSIONS = {}


def get_or_create_session():
    """
    Retrieves the current user's session data from server-side store or initializes it.
    """
    session_id = session.get("session_id")
    if not session_id or session_id not in INTERVIEW_SESSIONS:
        session_id = str(uuid.uuid4())
        session["session_id"] = session_id
        topic = session.get("topic", "OOP & Software Design")
        questions = session.get("selected_questions") or get_interview_questions(topic, 5)
        INTERVIEW_SESSIONS[session_id] = {
            "topic": topic,
            "questions": questions,
            "current_index": 0,
            "scores": [],
            "history": [],
            "last_evaluation": None,
            "final_result": None
        }
    return session_id, INTERVIEW_SESSIONS[session_id]


@interview_bp.route("/start", methods=["POST"])
def start_interview():
    """
    Initializes a new interview session with dynamic non-repeating questions.
    """
    topic = request.form.get("topic", "OOP & Software Design")
    try:
        question_count = int(request.form.get("count", 5))
    except (ValueError, TypeError):
        question_count = 5

    # Dynamically generate fresh questions using AI with random bank fallback
    selected_questions = get_interview_questions(topic, question_count, use_ai=True)

    session_id = str(uuid.uuid4())
    session["session_id"] = session_id
    session["topic"] = topic
    session.modified = True

    INTERVIEW_SESSIONS[session_id] = {
        "topic": topic,
        "questions": selected_questions,
        "current_index": 0,
        "scores": [],
        "history": [],
        "last_evaluation": None,
        "final_result": None
    }

    return redirect(url_for("interview.interview"))


@interview_bp.route("/interview", methods=["GET", "POST"])
def interview():
    session_id, data = get_or_create_session()
    questions = data["questions"]
    total_questions = len(questions)
    topic = data["topic"]

    if request.method == "POST":
        answer = request.form.get("answer", "").strip()
        try:
            submitted_number = int(request.form.get("number", data["current_index"]))
        except (ValueError, TypeError):
            submitted_number = data["current_index"]

        # Validate question index
        if 0 <= submitted_number < total_questions:
            question = questions[submitted_number]
        else:
            question = questions[min(data["current_index"], total_questions - 1)]

        # Evaluate via AI (with fallback)
        score, feedback_text = evaluate_answer(answer, question, topic=topic)

        # Record score and history
        eval_item = {
            "question_number": submitted_number + 1,
            "question": question,
            "answer": answer if answer else "(No answer provided)",
            "score": score,
            "feedback": feedback_text
        }

        # Prevent duplicate submissions for the same question index
        if submitted_number == len(data["scores"]):
            data["scores"].append(score)
            data["history"].append(eval_item)
        elif submitted_number < len(data["scores"]):
            data["scores"][submitted_number] = score
            data["history"][submitted_number] = eval_item
        else:
            data["scores"].append(score)
            data["history"].append(eval_item)

        data["last_evaluation"] = eval_item
        next_index = submitted_number + 1
        data["current_index"] = next_index

        # If there are more questions, show next question along with evaluation of previous answer
        if next_index < total_questions:
            return render_template(
                "interview.html",
                question=questions[next_index],
                number=next_index,
                total_questions=total_questions,
                topic=topic,
                last_evaluation=eval_item
            )

        # All questions answered - compute final diagnostic results
        total_score = sum(data["scores"])
        max_score = total_questions * 10
        percentage = round((total_score / max_score) * 100) if max_score > 0 else 0

        # Generate comprehensive overall AI feedback
        feedback = get_feedback(percentage, interview_history=data["history"], topic=topic)

        data["final_result"] = {
            "score": total_score,
            "max_score": max_score,
            "percentage": percentage,
            "performance": feedback["performance"],
            "strengths": feedback["strengths"],
            "weaknesses": feedback["weaknesses"],
            "suggestions": feedback["suggestions"],
            "history": data["history"],
            "topic": topic
        }

        return redirect(url_for("interview.result"))

    # GET request - do NOT reset! Show the question at current_index
    curr = data.get("current_index", 0)
    if curr >= total_questions and data.get("final_result"):
        return redirect(url_for("interview.result"))

    curr = min(curr, total_questions - 1)
    return render_template(
        "interview.html",
        question=questions[curr],
        number=curr,
        total_questions=total_questions,
        topic=topic,
        last_evaluation=data.get("last_evaluation")
    )


@interview_bp.route("/result", methods=["GET"])
def result():
    """
    Displays the final comprehensive performance and diagnostic report.
    """
    session_id, data = get_or_create_session()
    res = data.get("final_result")

    if not res:
        # If no result exists yet, redirect to interview
        return redirect(url_for("interview.interview"))

    return render_template(
        "result.html",
        score=res["score"],
        max_score=res["max_score"],
        percentage=res["percentage"],
        performance=res["performance"],
        strengths=res["strengths"],
        weaknesses=res["weaknesses"],
        suggestions=res["suggestions"],
        history=res["history"],
        topic=res["topic"]
    )