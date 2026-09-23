#!/usr/bin/env python3
"""
AI Technical Interview System - CLI Terminal Interface
Run interactive mock technical interviews directly in your terminal without any browser or URL.
"""

import sys
import os
import time

# Ensure UTF-8 output on Windows consoles to prevent encoding errors
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from dotenv import load_dotenv

# Initialize environment
load_dotenv()

from models.questions import QUESTION_BANKS, get_interview_questions
from models.evaluator import evaluate_answer, get_feedback

# ANSI Colors for terminal styling
CYAN = "\033[96m"
BLUE = "\033[94m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"


def print_banner():
    print(f"{CYAN}{BOLD}")
    print("=" * 64)
    print("       AI TECHNICAL INTERVIEW SIMULATOR (CLI MODE)      ")
    print("=" * 64)
    print(f"{RESET}")
    print(f"{DIM}Practice technical interviews directly in your terminal.{RESET}\n")


def choose_topic():
    topics = list(QUESTION_BANKS.keys())
    print(f"{BOLD}Select an Interview Topic:{RESET}")
    for idx, topic in enumerate(topics, 1):
        print(f"  {CYAN}[{idx}]{RESET} {topic}")
    
    while True:
        try:
            choice = input(f"\n{YELLOW}Enter topic number (1-{len(topics)}): {RESET}").strip()
            if not choice:
                continue
            idx = int(choice)
            if 1 <= idx <= len(topics):
                selected = topics[idx - 1]
                print(f"Selected: {GREEN}{BOLD}{selected}{RESET}\n")
                return selected
            print(f"{RED}Invalid number. Please choose between 1 and {len(topics)}.{RESET}")
        except ValueError:
            print(f"{RED}Please enter a valid number.{RESET}")


def choose_question_count(max_available):
    print(f"{BOLD}Select Number of Questions:{RESET}")
    print(f"  {CYAN}[1]{RESET} Quick Practice (3 Questions)")
    print(f"  {CYAN}[2]{RESET} Standard Interview (5 Questions)")
    print(f"  {CYAN}[3]{RESET} Deep Dive (10 Questions)")

    while True:
        choice = input(f"\n{YELLOW}Choose an option (1-3) [default: 1]: {RESET}").strip()
        if choice in ("", "1"):
            return 3
        elif choice == "2":
            return 5
        elif choice == "3":
            return min(10, max_available)
        else:
            print(f"{RED}Please enter 1, 2, or 3.{RESET}")


def get_answer():
    try:
        answer = input(f"{YELLOW}Your Answer: {RESET}").strip()
        return answer
    except (EOFError, KeyboardInterrupt):
        print()
        sys.exit(0)


def run_interview():
    print_banner()
    topic = choose_topic()
    available_questions = QUESTION_BANKS.get(topic, [])
    q_count = choose_question_count(len(available_questions))

    print(f"\n{CYAN}[Generating fresh, dynamic questions for this session...]{RESET}")
    selected_questions = get_interview_questions(topic, q_count, use_ai=True)

    interview_history = []
    total_score = 0

    print(f"\n{GREEN}{BOLD}Starting interview with {q_count} questions. Good luck!{RESET}")
    print("-" * 64)

    for i, q in enumerate(selected_questions, 1):
        print(f"\n{BOLD}{CYAN}Question {i} of {q_count}:{RESET}")
        print(f"{BOLD}{q}{RESET}\n")

        answer = ""
        while not answer:
            answer = get_answer()
            if not answer:
                print(f"{RED}Answer cannot be empty. Please enter your technical explanation.{RESET}")

        print(f"\n{DIM}[Evaluating answer with AI...]{RESET}")
        start_time = time.time()
        score, feedback = evaluate_answer(answer, q, topic=topic)
        elapsed = time.time() - start_time

        total_score += score
        interview_history.append({
            "question": q,
            "answer": answer,
            "score": score,
            "feedback": feedback
        })

        print(f"{GREEN}✓ Response recorded.{RESET} {DIM}(evaluated in {elapsed:.1f}s){RESET}")
        print("-" * 64)

    # Final overall evaluation
    max_possible = q_count * 10
    percentage = int((total_score / max_possible) * 100) if max_possible > 0 else 0

    print(f"\n{DIM}[Generating comprehensive diagnostic performance report...]{RESET}")
    feedback_report = get_feedback(percentage, interview_history=interview_history, topic=topic)

    # Display Results
    print("\n" + "=" * 64)
    print("             FINAL INTERVIEW PERFORMANCE REPORT          ")
    print("=" * 64)
    print(f"Target Domain:       {CYAN}{topic}{RESET}")
    print(f"Questions Attempted: {q_count}")
    print(f"Total Score:         {BOLD}{total_score} / {max_possible}{RESET} ({percentage}%)")
    print(f"Overall Result:      {BOLD}{feedback_report.get('performance', 'Completed')}{RESET}")
    print("=" * 64)

    print(f"\n{GREEN}{BOLD}Key Strengths:{RESET}")
    for item in feedback_report.get("strengths", []):
        print(f"  [+] {item}")

    print(f"\n{YELLOW}{BOLD}Areas to Improve:{RESET}")
    for item in feedback_report.get("weaknesses", []):
        print(f"  [-] {item}")

    print(f"\n{CYAN}{BOLD}Recommendations & Action Items:{RESET}")
    for item in feedback_report.get("suggestions", []):
        print(f"  [>] {item}")

    print("\n" + "-" * 64)
    print(f"{BOLD}Question-by-Question Detailed Feedback:{RESET}")
    print("-" * 64)
    for idx, item in enumerate(interview_history, 1):
        sc = item["score"]
        if sc >= 8:
            sc_color = GREEN
        elif sc >= 5:
            sc_color = YELLOW
        else:
            sc_color = RED

        print(f"\n{BOLD}{CYAN}Q{idx}: {item['question']}{RESET}")
        print(f"Score: {sc_color}{BOLD}{sc} / 10{RESET}")
        print(f"{DIM}Your Answer: {item['answer']}{RESET}")
        print(f"{GREEN}AI Feedback: {item['feedback']}{RESET}")

    print("\n" + "=" * 64)

    # Prompt to save report
    save = input(f"\n{YELLOW}Would you like to save this report to a file? (y/n) [default: n]: {RESET}").strip().lower()
    if save == "y":
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"interview_report_{timestamp}.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write("=" * 64 + "\n")
            f.write(f"AI TECHNICAL INTERVIEW REPORT - {topic}\n")
            f.write("=" * 64 + "\n\n")
            f.write(f"Overall Score: {total_score}/{max_possible} ({percentage}%)\n")
            f.write(f"Evaluation: {feedback_report.get('performance', 'Completed')}\n\n")
            f.write("Strengths:\n")
            for s in feedback_report.get("strengths", []):
                f.write(f" [+] {s}\n")
            f.write("\nAreas to Improve:\n")
            for w in feedback_report.get("weaknesses", []):
                f.write(f" [-] {w}\n")
            f.write("\nRecommendations:\n")
            for r in feedback_report.get("suggestions", []):
                f.write(f" [>] {r}\n")
            f.write("\n" + "-" * 64 + "\n")
            f.write("DETAILED QUESTION & ANSWER BREAKDOWN\n")
            f.write("-" * 64 + "\n")
            for idx, item in enumerate(interview_history, 1):
                f.write(f"\nQuestion {idx}: {item['question']}\n")
                f.write(f"Score: {item['score']}/10\n")
                f.write(f"Answer:\n{item['answer']}\n")
                f.write(f"Feedback: {item['feedback']}\n")
        print(f"{GREEN}Report successfully saved to {BOLD}{filename}{RESET}!")

    print(f"\n{CYAN}Thank you for practicing with AI Interview Simulator!{RESET}\n")


if __name__ == "__main__":
    try:
        run_interview()
    except KeyboardInterrupt:
        print(f"\n\n{YELLOW}Interview session cancelled. Goodbye!{RESET}\n")
        sys.exit(0)
