import os
from dotenv import load_dotenv
from flask import Flask, render_template
from routes.interview_routes import interview_bp

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "ai-interview-secure-session-key-2026")

@app.route("/")
def home():
    from models.questions import QUESTION_BANKS
    return render_template("index.html", topics=list(QUESTION_BANKS.keys()))

app.register_blueprint(interview_bp)

if __name__ == "__main__":
    app.run(debug=True)