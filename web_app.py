"""
Flask Web Application for the Safe Autonomous Code-Generation Self-Correcting Agent.
Provides an interactive web UI dashboard to execute tasks, view live execution flow,
inspect code/stdout/stderr per attempt, and demonstrate self-correction and timeout safety.
"""

import os
import sys
import time
import re
from flask import Flask, render_template, request, jsonify

# Add workspace root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from self_correcting_agent.agent import run_agent
from self_correcting_agent.tests import TASKS, DEMO_SELF_CORRECT_TASK, DEMO_TIMEOUT_TASK, DEMO_SECURITY_TASK

app = Flask(__name__, template_folder="templates", static_folder="static")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/preset_tasks", methods=["GET"])
def get_preset_tasks():
    presets = []
    for t in TASKS:
        presets.append({
            "id": f"task_{t['id']}",
            "name": t["name"],
            "task": t["task"],
            "type": "standard"
        })
    presets.append({
        "id": "demo_self_correct",
        "name": DEMO_SELF_CORRECT_TASK["name"],
        "task": DEMO_SELF_CORRECT_TASK["task"],
        "type": "demo_self_correct"
    })
    presets.append({
        "id": "demo_timeout",
        "name": DEMO_TIMEOUT_TASK["name"],
        "task": DEMO_TIMEOUT_TASK["task"],
        "type": "demo_timeout"
    })
    presets.append({
        "id": "demo_security",
        "name": DEMO_SECURITY_TASK["name"],
        "task": DEMO_SECURITY_TASK["task"],
        "type": "demo_security"
    })
    return jsonify({"status": "success", "presets": presets})


@app.route("/api/generate_prompt", methods=["POST"])
def generate_prompt():
    data = request.json or {}
    query = data.get("query", "").strip()

    if not query:
        return jsonify({"status": "error", "message": "Query cannot be empty"}), 400

    q_lower = query.lower()

    # Smart template mapping for common search terms
    if "anagram" in q_lower:
        task_text = """Write a function is_anagram(s1, s2) that checks if two strings are anagrams.

Required tests:
assert is_anagram("listen", "silent") is True
assert is_anagram("hello", "world") is False
print("All anagram tests passed!")"""
        fn_name = "is_anagram"

    elif "vowel" in q_lower:
        task_text = """Write a function count_vowels(s) that returns the number of vowels in a string s.

Required tests:
assert count_vowels("hello") == 2
assert count_vowels("sky") == 0
assert count_vowels("AEIOU") == 5
print("All vowel count tests passed!")"""
        fn_name = "count_vowels"

    elif "leap" in q_lower:
        task_text = """Write a function is_leap_year(year) that returns True if year is a leap year and False otherwise.

Required tests:
assert is_leap_year(2020) is True
assert is_leap_year(2021) is False
assert is_leap_year(2000) is True
assert is_leap_year(1900) is False
print("All leap year tests passed!")"""
        fn_name = "is_leap_year"

    elif "missing" in q_lower:
        task_text = """Write a function find_missing_number(nums) that finds the missing number from an array containing n distinct numbers from 0 to n.

Required tests:
assert find_missing_number([3, 0, 1]) == 2
assert find_missing_number([0, 1]) == 2
print("All missing number tests passed!")"""
        fn_name = "find_missing_number"

    elif "celsius" in q_lower or "fahrenheit" in q_lower or "temp" in q_lower:
        task_text = """Write a function celsius_to_fahrenheit(temp) that converts Celsius temperature to Fahrenheit.

Required tests:
assert celsius_to_fahrenheit(0) == 32
assert celsius_to_fahrenheit(100) == 212
assert celsius_to_fahrenheit(37) == 98.6
print("All temperature conversion tests passed!")"""
        fn_name = "celsius_to_fahrenheit"

    elif "transpose" in q_lower or "matrix" in q_lower:
        task_text = """Write a function matrix_transpose(matrix) that transposes a 2D matrix.

Required tests:
assert matrix_transpose([[1, 2], [3, 4]]) == [[1, 3], [2, 4]]
assert matrix_transpose([[1, 2, 3], [4, 5, 6]]) == [[1, 4], [2, 5], [3, 6]]
print("All matrix transpose tests passed!")"""
        fn_name = "matrix_transpose"

    elif "parentheses" in q_lower or "bracket" in q_lower:
        task_text = """Write a function is_valid_parentheses(s) that determines if input string containing brackets '()[]{}' is valid.

Required tests:
assert is_valid_parentheses("()") is True
assert is_valid_parentheses("()[]{}") is True
assert is_valid_parentheses("(]") is False
print("All valid parentheses tests passed!")"""
        fn_name = "is_valid_parentheses"

    elif "gcd" in q_lower or "greatest common" in q_lower:
        task_text = """Write a function gcd(a, b) that returns the greatest common divisor of a and b.

Required tests:
assert gcd(48, 18) == 6
assert gcd(101, 10) == 1
print("All GCD tests passed!")"""
        fn_name = "gcd"

    elif "lcm" in q_lower or "least common" in q_lower:
        task_text = """Write a function lcm(a, b) that returns the least common multiple of a and b.

Required tests:
assert lcm(4, 6) == 12
assert lcm(5, 7) == 35
print("All LCM tests passed!")"""
        fn_name = "lcm"

    elif "square" in q_lower:
        task_text = """Write a function square(n) that returns the square of n.

Required tests:
assert square(4) == 16
assert square(0) == 0
assert square(-3) == 9
print("All square tests passed!")"""
        fn_name = "square"

    elif "even" in q_lower or "odd" in q_lower:
        task_text = """Write a function is_even(n) that returns True if n is even and False otherwise.

Required tests:
assert is_even(4) is True
assert is_even(7) is False
assert is_even(0) is True
print("All even/odd tests passed!")"""
        fn_name = "is_even"

    else:
        # Dynamic fallback for any general query/question
        words = [w for w in re.sub(r'[^a-zA-Z0-9_\s]', '', q_lower).split() if w not in {'write', 'a', 'function', 'to', 'for', 'the', 'and', 'in', 'of', 'is'}]
        clean_fn = "_".join(words[:3]) if words else "custom_solution"
        task_text = f"""Write a function {clean_fn}(*args) to solve the problem: {query}.

Required tests:
assert {clean_fn}(1) is not None
print("All custom task tests passed!")"""
        fn_name = clean_fn

    return jsonify({
        "status": "success",
        "task": task_text,
        "func_name": fn_name,
        "query": query
    })


@app.route("/api/run_task", methods=["POST"])
def run_task_api():
    data = request.json or {}
    task_desc = data.get("task", "").strip()
    max_attempts = int(data.get("max_attempts", 3))
    timeout = int(data.get("timeout", 10))
    preset_type = data.get("preset_type", "custom")

    if not task_desc:
        return jsonify({"status": "error", "message": "Task description cannot be empty."}), 400

    start_time = time.time()

    mock_responses = None
    if preset_type == "demo_self_correct":
        mock_responses = DEMO_SELF_CORRECT_TASK["mock_responses"]
    elif preset_type == "demo_timeout":
        mock_responses = DEMO_TIMEOUT_TASK["mock_responses"]
        timeout = min(timeout, 3)
    elif preset_type == "demo_security":
        mock_responses = DEMO_SECURITY_TASK["mock_responses"]

    result = run_agent(
        task_description=task_desc,
        max_attempts=max_attempts,
        timeout=timeout,
        mock_responses=mock_responses
    )

    elapsed = round(time.time() - start_time, 2)
    result["elapsed_seconds"] = elapsed

    return jsonify({"status": "success", "data": result})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
