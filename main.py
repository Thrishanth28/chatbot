#!/usr/bin/env python3
"""
PyBot — Extended Rule-Based Chatbot
----------------------------------

This script expands on a basic rule-based chatbot and includes:
 - Many more instructions and intents
 - Command handling (/help, /history, /save, /load, /quiz, /clear, /exit)
 - Safe arithmetic evaluator (no direct eval of user code)
 - Conversation logging and persistence (JSON)
 - Mini-quiz and small games
 - Detailed comments and docstrings to help you learn/modify

Author: PyBot Example (you can customize)
License: MIT-style permissive usage for learning & non-commercial projects
"""

import ast
import json
import math
import operator
import random
import re
import sys
import time
from datetime import datetime, date

# --------------------------
# Configuration / Constants
# --------------------------
LOG_FILENAME = "pybot_chat_history.json"
QUIZ_QUESTIONS = [
    {
        "q": "What is the output of 2 + 2?",
        "a": "4"
    },
    {
        "q": "Which language is this bot written in?",
        "a": "python"
    },
    {
        "q": "What year has 365 days? (type: year)",
        "a": "any non-leap year"
    },
]
SMALL_FACTS = [
    "Honey never spoils — archaeologists found edible honey in ancient Egyptian tombs.",
    "Octopuses have three hearts.",
    "The Eiffel Tower can be 15 cm taller during the summer (thermal expansion)."
]

# Allowed operators for safe math eval
_ALLOWED_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.FloorDiv: operator.floordiv,
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}

# --------------------------
# Utility functions
# --------------------------


def typing_print(text, delay=0.0):
    """
    Prints text with an optional small typing delay between characters to mimic typing.
    Set delay to 0.0 for instant printing.
    """
    if delay <= 0:
        print(text)
        return
    for ch in text:
        sys.stdout.write(ch)
        sys.stdout.flush()
        time.sleep(delay)
    print()


def timestamp():
    """Return current timestamp string for logs."""
    return datetime.now().isoformat()


def safe_eval_expr(expr: str):
    """
    Safely evaluate arithmetic expressions using ast.

    Supported operators: +, -, *, /, //, %, **, unary +/-
    No function calls, no names, no attribute access.
    Raises ValueError for unsupported expressions.
    """
    expr = expr.strip()
    if not expr:
        raise ValueError("Empty expression")

    try:
        node = ast.parse(expr, mode="eval")
    except SyntaxError as e:
        raise ValueError(f"Invalid expression: {e}")

    def _eval(node):
        if isinstance(node, ast.Expression):
            return _eval(node.body)
        if isinstance(node, ast.Constant):  # Python 3.8+
            if isinstance(node.value, (int, float)):
                return node.value
            raise ValueError("Only numeric constants are allowed")
        if isinstance(node, ast.Num):  # older ast compatibility
            return node.n
        if isinstance(node, ast.BinOp):
            op_type = type(node.op)
            if op_type not in _ALLOWED_OPERATORS:
                raise ValueError(f"Operator {op_type} not supported")
            left = _eval(node.left)
            right = _eval(node.right)
            return _ALLOWED_OPERATORS[op_type](left, right)
        if isinstance(node, ast.UnaryOp):
            op_type = type(node.op)
            if op_type not in _ALLOWED_OPERATORS:
                raise ValueError(f"Unary operator {op_type} not supported")
            operand = _eval(node.operand)
            return _ALLOWED_OPERATORS[op_type](operand)
        # optionally support parentheses (they are represented by nested nodes)
        raise ValueError(f"Unsupported expression type: {type(node)}")

    return _eval(node)


# --------------------------
# Persistence (log/save/load)
# --------------------------
def save_history(history, filename=LOG_FILENAME):
    """Save conversation history (list of dicts) to a json file."""
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
        return True, f"Saved history to {filename}."
    except Exception as e:
        return False, f"Failed to save history: {e}"


def load_history(filename=LOG_FILENAME):
    """Load conversation history from a json file."""
    try:
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
        return True, data
    except FileNotFoundError:
        return False, f"No saved history found at {filename}."
    except Exception as e:
        return False, f"Failed to load history: {e}"


# --------------------------
# Chatbot response logic
# --------------------------
def chatbot_response(user_input: str, meta=None):
    """Return a chatbot response string based on user input and simple rules."""
    if meta is None:
        meta = {}

    # Normalize
    text = user_input.strip()
    lower = text.lower()

    # Command detection (slash commands processed outside usually)
    if lower.startswith("/"):
        return "Use bot commands directly (handled separately). Type /help for commands."

    # Greeting
    if re.search(r"\b(hi|hello|hey|hiya|sup)\b", lower):
        return random.choice([
            "Hi there! 👋 How can I help you today?",
            "Hello! I'm PyBot 🤖 — ask me for /help to see what I can do.",
            "Hey! Nice to meet you. What would you like to do?"
        ])

    # Farewell
    if re.search(r"\b(bye|goodbye|see ya|see you|later)\b", lower):
        return random.choice([
            "Goodbye! Have a wonderful day! 👋",
            "See you later — come back if you need anything else!",
            "Bye! Stay curious ✨"
        ])

    # Thanks
    if re.search(r"\b(thanks|thank you|thx)\b", lower):
        return random.choice([
            "You're welcome! 😊",
            "Anytime — glad to help!",
            "No problem! If you'd like, type /help for more commands."
        ])

    # How are you
    if re.search(r"\bhow are you\b", lower):
        return "I'm just a set of Python instructions, but I'm running smoothly! 😊"

    # Name inquiry
    if re.search(r"\b(your name|who are you)\b", lower):
        return "I'm PyBot — your friendly rule-based chatbot assistant. You can call me PyBot 🤖"

    # Date/time
    if re.search(r"\b(time|current time|what time)\b", lower):
        return f"The current time is {datetime.now().strftime('%I:%M %p')} ⏰"
    if re.search(r"\b(date|today's date|what date)\b", lower):
        return f"Today's date is {date.today().strftime('%B %d, %Y')} 📅"

    # Jokes
    if "joke" in lower:
        jokes = [
            "Why did the computer show up late to work? It had a hard drive! 😂",
            "Why do programmers prefer dark mode? Because light attracts bugs! 🐛",
            "Why did the developer go broke? Because he used up all his cache. 💸"
        ]
        return random.choice(jokes)

    # Small facts
    if "fact" in lower or "random fact" in lower:
        return random.choice(SMALL_FACTS)

    # Simple math expression detection
    math_match = re.match(r"^calc[: ]+(.+)", lower)
    if math_match:
        expr = math_match.group(1)
        try:
            result = safe_eval_expr(expr)
            return f"Result: {result}"
        except Exception as e:
            return f"Calculator error: {e}"

    # Straight math input if user types only expression
    if re.fullmatch(r"[0-9\s\.\+\-\*\/\%\(\)\^//]+", lower.replace("^", "**")):
        # replace caret with power operator if used
        expr = lower.replace("^", "**")
        try:
            result = safe_eval_expr(expr)
            return f"Result: {result}"
        except Exception:
            # If not a valid math expression, continue
            pass

    # Sentiment-ish reply using simple keywords
    if re.search(r"\b(sad|down|unhappy|depressed)\b", lower):
        return "I'm sorry you're feeling that way. If you want, tell me what's on your mind — I can listen. 💬"
    if re.search(r"\b(happy|great|awesome|good|fantastic)\b", lower):
        return "That's wonderful to hear! Keep that momentum going! 🎉"

    # Small Q&A / FAQs
    faqs = {
        "what can you do": "I can chat, do safe math (prefix 'calc '), tell jokes, run a mini-quiz (/quiz), and save/load chat logs.",
        "how to exit": "Type /exit or press Ctrl+C to quit.",
        "how to save": "Use /save to write the conversation to a file.",
    }
    for q, a in faqs.items():
        if q in lower:
            return a

    # If user asks for quiz-related text
    if "quiz" in lower:
        return "Type /quiz to start a mini-quiz (multiple short questions)."

    # Fallback: suggest commands
    fallback_suggestions = [
        "Sorry, I didn’t understand that. Try /help to see options.",
        "I can respond to basic phrases or run commands like /quiz or /save — try them!",
        "If you want to compute something, type: calc 12/(3+1)"
    ]
    return random.choice(fallback_suggestions)


# --------------------------
# Command handlers
# --------------------------
def show_help():
    """Return help text explaining available commands and usage."""
    help_text = """
PyBot Commands and Usage
------------------------
General chat: type messages naturally, e.g., "hello", "your name", "tell me a joke".

Slash commands:
  /help       - Show this help message
  /history    - Show recent conversation history in memory
  /save       - Save conversation history to a file (pybot_chat_history.json)
  /load       - Load conversation history from file (merges into current session)
  /quiz       - Start a mini quiz
  /clear      - Clear in-memory conversation history
  /exit       - Exit the chatbot

Special features:
  calc <expr> - Safe arithmetic evaluation, e.g. "calc 2+3*4" or just "2+3*4"
               Supported: + - * / // % ** and parentheses.

Tips:
 - Be polite, but not necessary. I respond to keywords.
 - If I fail to understand, try rephrasing or use /help.
"""
    return help_text.strip()


# --------------------------
# Mini-Quiz flow
# --------------------------
def run_quiz(history):
    """Run a mini-quiz using QUIZ_QUESTIONS. Records results in history."""
    typing_print("Starting a mini-quiz. Answer the questions. Type 'skip' to skip a question.", 0.002)
    score = 0
    total = len(QUIZ_QUESTIONS)
    for idx, q in enumerate(QUIZ_QUESTIONS, start=1):
        typing_print(f"Q{idx}: {q['q']}", 0.002)
        answer = input("Your answer: ").strip().lower()
        if answer == "skip":
            typing_print("Skipped.", 0.002)
            history.append({"time": timestamp(), "sender": "user", "text": f"quiz q{idx} skip"})
            history.append({"time": timestamp(), "sender": "bot", "text": "Question skipped."})
            continue
        if answer == q["a"].lower():
            typing_print("Correct! ✅", 0.002)
            history.append({"time": timestamp(), "sender": "user", "text": f"quiz q{idx} {answer}"})
            history.append({"time": timestamp(), "sender": "bot", "text": "Correct!"})
            score += 1
        else:
            typing_print(f"Not quite. The expected answer was: {q['a']}", 0.002)
            history.append({"time": timestamp(), "sender": "user", "text": f"quiz q{idx} {answer}"})
            history.append({"time": timestamp(), "sender": "bot", "text": f"Answer: {q['a']}"})
    typing_print(f"Quiz complete. Score: {score}/{total}")
    return score, total


# --------------------------
# Main chat loop
# --------------------------
def main():
    # In-memory conversation history as list of dicts
    history = []

    # Welcome message and short instructions
    typing_print("🤖 PyBot: Hello! I'm PyBot — your friendly rule-based assistant.", 0.001)
    typing_print("Type '/help' for a list of commands. Type '/exit' or 'bye' to quit.\n", 0.001)

    # Interactive loop
    try:
        while True:
            user_input = input("You: ").strip()
            if not user_input:
                # ignore empty input but record it
                history.append({"time": timestamp(), "sender": "user", "text": ""})
                print("🤖 PyBot: (I didn't catch that — say something or type /help.)")
                continue

            # Record user message
            history.append({"time": timestamp(), "sender": "user", "text": user_input})

            # Slash-command handling
            if user_input.startswith("/"):
                cmd = user_input.strip().lower()
                if cmd == "/help":
                    help_text = show_help()
                    history.append({"time": timestamp(), "sender": "bot", "text": help_text})
                    print(help_text)
                    continue
                if cmd == "/history":
                    # Show last 20 messages for brevity
                    last = history[-40:]
                    for entry in last:
                        ts = entry.get("time", "")
                        who = entry.get("sender", "user")
                        text = entry.get("text", "")
                        print(f"[{ts}] {who}: {text}")
                    continue
                if cmd == "/save":
                    ok, msg = save_history(history)
                    history.append({"time": timestamp(), "sender": "bot", "text": msg})
                    print(msg)
                    continue
                if cmd == "/load":
                    ok, data = load_history()
                    if ok:
                        # merge histories
                        history.extend(data)
                        msg = f"Loaded and merged {len(data)} entries from file."
                        history.append({"time": timestamp(), "sender": "bot", "text": msg})
                        print(msg)
                    else:
                        history.append({"time": timestamp(), "sender": "bot", "text": data})
                        print(data)
                    continue
                if cmd == "/clear":
                    history.clear()
                    msg = "In-memory history cleared."
                    print(msg)
                    history.append({"time": timestamp(), "sender": "bot", "text": msg})
                    continue
                if cmd == "/quiz":
                    history.append({"time": timestamp(), "sender": "bot", "text": "Starting quiz."})
                    score, total = run_quiz(history)
                    summary = f"Quiz finished. Score: {score}/{total}"
                    history.append({"time": timestamp(), "sender": "bot", "text": summary})
                    print(summary)
                    continue
                if cmd == "/exit":
                    print("🤖 PyBot: Goodbye! 👋")
                    history.append({"time": timestamp(), "sender": "bot", "text": "Goodbye!"})
                    # attempt to save automatically
                    save_history(history)
                    break
                # Unknown command
                msg = "Unknown command. Type /help for available commands."
                print(msg)
                history.append({"time": timestamp(), "sender": "bot", "text": msg})
                continue

            # Non-command flow: get response from main logic
            response = chatbot_response(user_input)
            # Record bot response
            history.append({"time": timestamp(), "sender": "bot", "text": response})

            # Simulated typing for the bot
            typing_print(f"🤖 PyBot: {response}", 0.000)
            # Quick auto-save hint: not automatic saving to file every message to avoid IO overhead

            # If user said bye in free text, exit politely
            if re.search(r"\b(bye|goodbye|see ya|see you|later)\b", user_input.lower()):
                print("🤖 PyBot: It was great chatting. I'll save this conversation to disk.")
                save_history(history)
                break

    except KeyboardInterrupt:
        # Graceful exit on Ctrl+C
        print("\n\n🤖 PyBot: Received keyboard interrupt. Saving conversation and exiting...")
        save_history(history)
    except Exception as e:
        # Catch-all for unexpected errors
        print(f"\n🤖 PyBot: Oops — encountered an error: {e}")
        save_history(history)


if __name__ == "__main__":
    main()
