import os
import re
import json
import random
from typing import List

# Comprehensive Question Banks with 15+ curated questions per category for randomized fallback
QUESTION_BANKS = {
    "OOP & Software Design": [
        "What is Object-Oriented Programming and what are its four core pillars?",
        "What is inheritance in OOP, and what is the difference between single and multiple inheritance?",
        "What is polymorphism? Explain method overloading vs method overriding with practical examples.",
        "What is encapsulation and how does it help in data hiding and maintenance?",
        "What is the difference between an Abstract Class and an Interface? When would you use which?",
        "Explain the SOLID principles with a specific focus on the Single Responsibility and Open/Closed principles.",
        "What is the Dependency Inversion Principle and how does Dependency Injection implement it?",
        "Explain the difference between Composition and Inheritance. Why is 'Composition over Inheritance' often recommended?",
        "What is the Singleton design pattern? What problems can it introduce in large codebases?",
        "Explain the Factory Method pattern and how it decouples object creation from business logic.",
        "What is the Observer pattern and where is it commonly applied in event-driven systems?",
        "How do you design a thread-safe class in an object-oriented environment?",
        "What are cohesion and coupling in software architecture? Why do we aim for high cohesion and low coupling?",
        "Explain the concept of immutability in object design and why it is beneficial in concurrent applications.",
        "How would you refactor a large 'God Object' class into smaller, maintainable components?"
    ],
    "Python Developer": [
        "Explain how memory management and garbage collection (reference counting & cyclic GC) work in Python.",
        "What are Python decorators and in what practical scenarios would you implement custom decorators?",
        "What is the difference between list, tuple, and set in Python in terms of mutability, performance, and hashing?",
        "Explain the Global Interpreter Lock (GIL) and its implications for CPU-bound vs I/O-bound multi-threaded programs.",
        "What are Python generators, how does the 'yield' keyword work, and why are they memory efficient?",
        "What is the difference between shallow copy and deep copy in Python? Give an example using nested data structures.",
        "Explain how `*args` and `**kwargs` work in function definitions and argument unpacking.",
        "What are Python context managers and how do the `__enter__` and `__exit__` magic methods work?",
        "What is the difference between `@classmethod`, `@staticmethod`, and regular instance methods?",
        "Explain Python's method resolution order (MRO) and the C3 linearization algorithm in multiple inheritance.",
        "How does Python's `asyncio` event loop differ from traditional multi-threading and multi-processing?",
        "What are Python dataclasses and how do they differ from `namedtuple` and standard classes?",
        "How would you profile and optimize a slow Python function that processes millions of rows of data?",
        "Explain how Python handles exception propagation and the difference between `except Exception:` and `except BaseException:`.",
        "What are Python metaclasses and what is a legitimate use case for them in framework design?"
    ],
    "Web & Fullstack": [
        "Explain the differences between RESTful APIs and GraphQL. What are the trade-offs of each?",
        "What is CORS (Cross-Origin Resource Sharing), why is it enforced, and how do you resolve CORS errors correctly?",
        "What is the difference between SQL and NoSQL databases? When would you choose one over the other?",
        "Explain how authentication works using JWT (JSON Web Tokens) versus session-based cookie authentication.",
        "What strategies do you use to optimize the load time, Core Web Vitals, and runtime performance of a web application?",
        "Explain the concept of database indexing. How does a B-Tree index work and what are the trade-offs of having too many indexes?",
        "What is the difference between Server-Side Rendering (SSR) and Client-Side Rendering (CSR)?",
        "How do you protect a web application against SQL Injection, Cross-Site Scripting (XSS), and Cross-Site Request Forgery (CSRF)?",
        "Explain how Redis or Memcached is used for caching in web architectures. What are cache invalidation strategies?",
        "What is a WebSocket connection and how does it differ from HTTP polling and Server-Sent Events (SSE)?",
        "Explain the concept of database transactions, ACID properties, and isolation levels.",
        "How do you design an API that handles pagination, filtering, and sorting gracefully?",
        "What is rate limiting in web APIs and what algorithms (e.g. token bucket, sliding window) are used to enforce it?",
        "Explain the role of reverse proxies like Nginx in load balancing, SSL termination, and static asset delivery.",
        "How do you handle background asynchronous processing (e.g., Celery, RabbitMQ, Redis Queue) in a web backend?"
    ],
    "Data Structures & Algorithms": [
        "What is the difference between an Array and a Singly/Doubly Linked List in terms of memory layout and Big-O complexity?",
        "Explain how a Hash Table works internally, how collisions are resolved, and what causes worst-case O(N) performance.",
        "What is the difference between Breadth-First Search (BFS) and Depth-First Search (DFS)? Give typical use cases for each.",
        "Explain the concept of Big-O notation, including time and space complexity, and compare O(log N), O(N), and O(N log N).",
        "What is dynamic programming and how does top-down memoization differ from bottom-up tabulation?",
        "Explain how QuickSort and MergeSort work. Why is MergeSort preferred for linked lists while QuickSort is often faster for arrays in-place?",
        "What is a Binary Search Tree (BST) and what is the advantage of self-balancing trees like AVL or Red-Black trees?",
        "How does a Min-Heap / Max-Heap work and how is it used to implement an efficient Priority Queue?",
        "Explain Dijkstra's algorithm for shortest paths in a weighted graph. When does it fail (e.g., negative weights)?",
        "What is the Two-Pointer technique and in what types of array/string problems is it most effective?",
        "Explain the Sliding Window technique with an example problem like finding the maximum sum subarray of size K.",
        "What is a Trie (Prefix Tree) and why is it ideal for autocomplete search engines?",
        "How do you detect a cycle in a linked list using Floyd's Tortoise and Hare algorithm?",
        "What is a Topological Sort and how is it used in dependency resolution (e.g. build systems, package managers)?",
        "Explain the difference between greedy algorithms and dynamic programming. When does a greedy approach fail?"
    ],
    "Behavioral & HR": [
        "Tell me about a challenging technical bug or outage you resolved. What was your systematic debugging approach?",
        "Describe a situation where you had a strong technical disagreement with a team member. How did you handle and resolve it?",
        "How do you prioritize your engineering tasks when managing tight deadlines and competing stakeholder requests?",
        "Tell me about a time you had to learn a completely new technology, tool, or framework quickly to deliver a project.",
        "Why are you interested in this role and where do you see your technical career progressing over the next 2-3 years?",
        "Describe a project you worked on that failed or did not meet expectations. What did you learn from the experience?",
        "How do you handle receiving critical feedback on a code review or architecture proposal?",
        "Tell me about a time you had to explain a complex technical concept to a non-technical stakeholder or client.",
        "How do you approach mentoring junior developers or onboarding new team members into an existing codebase?",
        "Describe a situation where you noticed technical debt accumulating in a codebase. How did you advocate for addressing it?",
        "Tell me about a time you took the initiative to improve a development process, CI/CD pipeline, or testing workflow.",
        "How do you balance delivering features rapidly versus writing clean, maintainable, and well-tested code?",
        "Describe a situation where project requirements changed drastically mid-development. How did you adapt?",
        "Tell me about an engineering achievement you are most proud of and what made it particularly rewarding.",
        "What habits or resources do you rely on to stay up-to-date with evolving software engineering standards and technologies?"
    ]
}

# Default list for backward compatibility
questions = QUESTION_BANKS["OOP & Software Design"]
default_questions = questions


def extract_json_array(raw_text: str) -> List[str]:
    """
    Safely extract a JSON array of question strings from LLM text,
    handling markdown blocks or surrounding text.
    """
    text = raw_text.strip()
    # Match outermost square brackets
    match = re.search(r"\[.*\]", text, re.DOTALL)
    if match:
        text = match.group(0)
    data = json.loads(text)
    if isinstance(data, list):
        cleaned = [str(item).strip() for item in data if str(item).strip()]
        return cleaned
    return []


def generate_ai_questions(topic: str, count: int = 5) -> List[str]:
    """
    Dynamically generates fresh, scenario-based technical interview questions
    using the configured AI model (Groq / Grok).
    Returns an empty list on failure so the caller can fall back cleanly.
    """
    try:
        from models.evaluator import get_grok_config
        client, model, _ = get_grok_config()
        if not client:
            return []

        prompt = f"""You are a principal technical interviewer at a top technology company.
Generate {count} unique, insightful, and practical interview questions for the topic: "{topic}".

Guidelines:
- Each question must be distinct, thought-provoking, and practical (avoid trivial yes/no or pure syntax queries).
- Vary between fundamental concepts, real-world architecture scenarios, and problem-solving.
- Return ONLY a valid JSON array containing exactly {count} string questions.
- No markdown preamble, explanations, or numbering outside the JSON list.

Example format:
[
  "Question 1 text here?",
  "Question 2 text here?"
]
"""
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert technical interviewer. Output strictly valid JSON arrays of strings."
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.75,
            max_tokens=600,
            timeout=10.0
        )

        raw_output = response.choices[0].message.content or ""
        generated = extract_json_array(raw_output)

        if len(generated) >= count:
            return generated[:count]
        elif len(generated) > 0:
            return generated
    except Exception as e:
        print(f"[AI Question Generator] Notice: AI question generation fallback triggered ({e})")

    return []


def get_interview_questions(topic: str, count: int = 5, use_ai: bool = True) -> List[str]:
    """
    Smart hybrid question selector:
    1. If use_ai is True, attempts to dynamically generate fresh questions using AI.
    2. If AI is unavailable or produces insufficient questions, randomly samples
       distinct questions from the expanded 15+ item question bank.
    3. Guarantees that questions change and vary on every interview session.
    """
    # 1. Try AI dynamic generation
    if use_ai:
        ai_questions = generate_ai_questions(topic, count=count)
        if len(ai_questions) >= count:
            return ai_questions

    # 2. Fallback: Random sampling from the comprehensive bank
    bank = QUESTION_BANKS.get(topic, default_questions)
    pool = list(bank)

    # If count is less than pool size, take a random sample without replacement
    if count <= len(pool):
        selected = random.sample(pool, count)
    else:
        # If user requested more than pool size, shuffle pool and loop
        random.shuffle(pool)
        selected = pool[:count]

    # Additional safety: ensure randomized ordering
    random.shuffle(selected)
    return selected