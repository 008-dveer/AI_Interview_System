from flask import Flask, render_template
from routes.interview_routes import interview_bp

app = Flask(__name__)

app.secret_key = "ai-interview-secret-key"

@app.route("/")
def home():
    return render_template("index.html")

app.register_blueprint(interview_bp)

if __name__ == "__main__":
    app.run(debug=True)