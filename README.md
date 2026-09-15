# 🤖 AI Technical Interview Preparation System

An interactive, AI-powered technical interview simulator built with **Python (Flask)**, **Groq AI / OpenAI SDK**, and a modern **Glassmorphic UI**. Candidates can practice technical interviews across multiple engineering disciplines, answer questions using text or **voice (Speech-to-Text)**, and receive real-time granular evaluation scores, constructive feedback, and a printable diagnostic performance report.

---

## ✨ Key Features

- **⚡ Lightning-Fast AI Evaluation**: Powered by Groq's high-speed inference engine (`openai/gpt-oss-120b` / `llama-3.3`) for sub-second evaluations.
- **🎯 Multiple Technical Domains**:
  - 🧱 Object-Oriented Programming (OOP) & System Design
  - 🐍 Python Developer Fundamentals
  - 🌐 Web & Fullstack Development
  - ⚡ Data Structures & Algorithms (DSA)
  - 💼 Behavioral & HR Scenario Questions
- **🎙️ Voice Input (Speech-to-Text)**: Speak your answers aloud just like in a real interview using the native browser Web Speech API.
- **📊 Granular Scoring & Diagnostics**:
  - Question-by-question scoring (0–10) and feedback.
  - Overall proficiency score (%) and executive summary.
  - Identification of key strengths, growth areas, and practical recommendations.
- **🖨️ PDF & Print Export**: One-click printable diagnostic report formatted cleanly for review or sharing.
- **🛡️ Resilient Fallback Engine**: If an API key is missing or internet disconnects, the app automatically switches to rule-based keyword evaluation without crashing.

---

## 📁 Project Structure

```
AI_Interview_System/
├── app.py                      # Flask application entry point
├── requirements.txt            # Python dependencies
├── .env.example                # Example environment variables template
├── .env                        # Local environment variables (API keys)
├── .gitignore                  # Git ignore rules for credentials & caches
│
├── models/
│   ├── evaluator.py            # AI evaluation engine with Groq & fallback logic
│   └── questions.py            # Multi-topic interview question banks
│
├── routes/
│   └── interview_routes.py     # Blueprint for interview flow, session & scoring
│
└── templates/
    ├── index.html              # Modern homepage with domain & length selection
    ├── interview.html          # Interactive question UI with voice mode & progress
    └── result.html             # Diagnostic report card with PDF export
```

---

## 🚀 Quickstart Guide

### 1. Prerequisites
- **Python 3.10+** installed on your system.
- An API key from **[Groq Cloud](https://console.groq.com/keys)** (Free tier available) or **[xAI](https://console.x.ai/)**.

---

### 2. Clone or Open the Repository
```bash
git clone https://github.com/your-username/AI_Interview_System.git
cd AI_Interview_System
```

---

### 3. Create & Activate a Virtual Environment (Optional but Recommended)

- **On Windows (PowerShell):**
  ```powershell
  python -m venv .venv
  .\.venv\Scripts\Activate.ps1
  ```

- **On macOS / Linux:**
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  ```

---

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

---

### 5. Configure Your API Key

1. Copy the `.env.example` file to create your `.env` file:
   ```bash
   cp .env.example .env
   ```
   *(On Windows Command Prompt: `copy .env.example .env`)*

2. Open [.env](file:///.env) and enter your API key:
   ```env
   GROK_API_KEY=gsk_your_groq_api_key_here
   ```

> **Note**: Both **Groq Cloud keys** (`gsk_...`) and **xAI Grok keys** (`xai-...`) are automatically recognized.

---

### 6. Run the Application
```bash
python app.py
```

You should see output similar to:
```
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
```

---

### 7. Access in Browser
Open your browser and navigate to:
```
http://127.0.0.1:5000
```

1. Select your target domain (e.g. *Python Developer*, *OOP*, *DSA*).
2. Choose question count (3 or 5 questions).
3. Click **Begin Technical Interview**.
4. Type or speak your answers and view your comprehensive AI report at the end!

---

## 🔑 How to Get a Free Groq API Key

1. Visit **[Groq Cloud Console](https://console.groq.com/keys)**.
2. Sign in with your Google or GitHub account.
3. Click **Create API Key**.
4. Copy the generated key (starts with `gsk_...`) and paste it into your `.env` file.

---

## 🛠️ Technology Stack

| Component | Technology |
| :--- | :--- |
| **Backend** | Python 3, Flask |
| **AI Inference** | Groq Cloud / OpenAI Python SDK |
| **Frontend** | HTML5, Modern Vanilla CSS (Glassmorphism), JavaScript |
| **Voice Mode** | Web Speech API (`webkitSpeechRecognition`) |
| **State Management** | Flask Secure Client Sessions |

---

## 📄 License
This project is open-source and available under the [MIT License](LICENSE).
