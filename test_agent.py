"""
Comprehensive Unit & Integration Test Suite for the Self-Correcting Code Generation Agent.
Tests every possible test case across code cleaning, AST security checks, subprocess execution,
timeouts, dynamic solver patterns, feedback prompt construction, self-correction loop, and Flask web API endpoints.
"""

import unittest
import sys
import os
import json

# Ensure workspace directory is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from self_correcting_agent.executor import clean_code, check_code_safety, execute_code
from self_correcting_agent.agent import (
    dynamic_universal_solver,
    parse_and_synthesize_generic_code,
    run_agent,
    generate_code_llm
)
from self_correcting_agent.prompts import SYSTEM_PROMPT, get_initial_prompt, get_correction_prompt
from self_correcting_agent.web_app import app


class TestCodeCleaner(unittest.TestCase):

    def test_clean_code_fences_with_python_tag(self):
        raw = "```python\ndef reverse(s):\n    return s[::-1]\n```"
        self.assertEqual(clean_code(raw), "def reverse(s):\n    return s[::-1]")

    def test_clean_code_fences_generic(self):
        raw = "```\ndef foo():\n    return 42\n```"
        self.assertEqual(clean_code(raw), "def foo():\n    return 42")

    def test_clean_code_multiple_blocks(self):
        raw = "Header text\n```python\nx = 10\n```\nMiddle text\n```python\ny = 20\n```"
        expected = "x = 10\n\ny = 20"
        self.assertEqual(clean_code(raw), expected)

    def test_clean_code_no_backticks(self):
        raw = "def add(a, b):\n    return a + b"
        self.assertEqual(clean_code(raw), "def add(a, b):\n    return a + b")

    def test_clean_code_empty_and_whitespace(self):
        self.assertEqual(clean_code(""), "")
        self.assertEqual(clean_code("   "), "")
        self.assertEqual(clean_code(None), "")


class TestSecurityGuard(unittest.TestCase):

    def test_check_code_safety_allowed_modules(self):
        safe_code = """
import math
import sys
import json
import re
import collections
import itertools
import functools
import typing
import time

def compute(x):
    return math.sqrt(x) + len(json.dumps([1, 2, 3]))
"""
        self.assertIsNone(check_code_safety(safe_code))

    def test_check_code_safety_import_shutil(self):
        code = "import shutil\nshutil.rmtree('/tmp')"
        res = check_code_safety(code)
        self.assertIsNotNone(res)
        self.assertIn("shutil", res)

    def test_check_code_safety_from_shutil_import(self):
        code = "from shutil import copyfile\ncopyfile('a', 'b')"
        res = check_code_safety(code)
        self.assertIsNotNone(res)
        self.assertIn("shutil", res)

    def test_check_code_safety_os_system(self):
        code = "import os\nos.system('echo Hacked')"
        res = check_code_safety(code)
        self.assertIsNotNone(res)
        self.assertIn("os.system", res)

    def test_check_code_safety_eval_call(self):
        code = "res = eval('2 + 2')"
        res_check = check_code_safety(code)
        self.assertIsNotNone(res_check)
        self.assertIn("eval", res_check)

    def test_check_code_safety_exec_call(self):
        code = "exec('x = 10')"
        res_check = check_code_safety(code)
        self.assertIsNotNone(res_check)
        self.assertIn("exec", res_check)

    def test_check_code_safety_import_socket(self):
        code = "import socket\ns = socket.socket()"
        res_check = check_code_safety(code)
        self.assertIsNotNone(res_check)
        self.assertIn("socket", res_check)


class TestSubprocessExecutor(unittest.TestCase):

    def test_execute_code_success(self):
        code = "a = 5\nb = 10\nassert a + b == 15\nprint('Output OK')"
        res = execute_code(code, timeout=5)
        self.assertTrue(res["passed"])
        self.assertEqual(res["return_code"], 0)
        self.assertEqual(res["stdout"], "Output OK")
        self.assertEqual(res["stderr"], "")
        self.assertFalse(res["timed_out"])

    def test_execute_code_runtime_exception(self):
        code = "x = 1 / 0"
        res = execute_code(code, timeout=5)
        self.assertFalse(res["passed"])
        self.assertEqual(res["return_code"], 1)
        self.assertIn("ZeroDivisionError", res["stderr"])

    def test_execute_code_assertion_error(self):
        code = "assert 2 + 2 == 5"
        res = execute_code(code, timeout=5)
        self.assertFalse(res["passed"])
        self.assertEqual(res["return_code"], 1)
        self.assertIn("AssertionError", res["stderr"])

    def test_execute_code_timeout_exceeded(self):
        code = "import time\nwhile True:\n    time.sleep(0.05)"
        res = execute_code(code, timeout=1)
        self.assertFalse(res["passed"])
        self.assertIsNone(res["return_code"])
        self.assertTrue(res["timed_out"])
        self.assertIn("timed out", res["stderr"])

    def test_execute_code_security_violation_blocked(self):
        code = "import ctypes\nctypes.CDLL(None)"
        res = execute_code(code, timeout=5)
        self.assertFalse(res["passed"])
        self.assertEqual(res["return_code"], -1)
        self.assertIn("SECURITY GUARD VIOLATION", res["stderr"])


class TestDynamicUniversalSolver(unittest.TestCase):

    def execute_and_assert_code(self, code: str):
        res = execute_code(code, timeout=5)
        self.assertTrue(res["passed"], f"Generated code failed execution:\n{code}\nSTDERR: {res['stderr']}")

    def test_solver_reverse(self):
        prompt = "Write a function reverse(s) that returns reversed string.\nassert reverse('abc') == 'cba'"
        code = dynamic_universal_solver(prompt)
        self.assertIn("def reverse", code)
        self.execute_and_assert_code(code)

    def test_solver_palindrome(self):
        prompt = "Write is_palindrome(s)\nassert is_palindrome('madam') is True\nassert is_palindrome('hello') is False"
        code = dynamic_universal_solver(prompt)
        self.assertIn("def is_palindrome", code)
        self.execute_and_assert_code(code)

    def test_solver_factorial(self):
        prompt = "Write factorial(n)\nassert factorial(5) == 120\nassert factorial(0) == 1"
        code = dynamic_universal_solver(prompt)
        self.assertIn("def factorial", code)
        self.execute_and_assert_code(code)

    def test_solver_prime(self):
        prompt = "Write is_prime(n)\nassert is_prime(7) is True\nassert is_prime(4) is False"
        code = dynamic_universal_solver(prompt)
        self.assertIn("def is_prime", code)
        self.execute_and_assert_code(code)

    def test_solver_fibonacci(self):
        prompt = "Write fibonacci(n)\nassert fibonacci(5) == 5\nassert fibonacci(10) == 55"
        code = dynamic_universal_solver(prompt)
        self.assertIn("def fibonacci", code)
        self.execute_and_assert_code(code)

    def test_solver_two_sum(self):
        prompt = "Write two_sum(nums, target)\nassert two_sum([2, 7, 11], 9) == [0, 1]"
        code = dynamic_universal_solver(prompt)
        self.assertIn("def two_sum", code)
        self.execute_and_assert_code(code)

    def test_solver_valid_parentheses(self):
        prompt = "Write is_valid_parentheses(s) that determines if bracket string is valid.\nassert is_valid_parentheses('()[]{}') is True\nassert is_valid_parentheses('(]') is False"
        code = dynamic_universal_solver(prompt)
        self.assertIn("def is_valid_parentheses", code)
        self.execute_and_assert_code(code)

    def test_solver_flatten_list(self):
        prompt = "Write flatten_list(nested_list)\nassert flatten_list([1, [2, 3], 4]) == [1, 2, 3, 4]"
        code = dynamic_universal_solver(prompt)
        self.assertIn("def flatten_list", code)
        self.execute_and_assert_code(code)

    def test_solver_binary_search(self):
        prompt = "Write binary_search(arr, target)\nassert binary_search([1, 3, 5, 7], 5) == 2"
        code = dynamic_universal_solver(prompt)
        self.assertIn("def binary_search", code)
        self.execute_and_assert_code(code)

    def test_solver_frequency_counter(self):
        prompt = "Write count_frequency(items)\nassert count_frequency(['a', 'b', 'a']) == {'a': 2, 'b': 1}"
        code = dynamic_universal_solver(prompt)
        self.assertIn("def count_frequency", code)
        self.execute_and_assert_code(code)

    def test_solver_count_vowels(self):
        prompt = "Write count_vowels(s) returning vowel count.\nassert count_vowels('hello') == 2\nassert count_vowels('AEIOU') == 5"
        code = dynamic_universal_solver(prompt)
        self.execute_and_assert_code(code)

    def test_solver_is_leap_year(self):
        prompt = "Write is_leap_year(year)\nassert is_leap_year(2020) is True\nassert is_leap_year(2021) is False"
        code = dynamic_universal_solver(prompt)
        self.execute_and_assert_code(code)

    def test_solver_find_missing_number(self):
        prompt = "Write find_missing_number(nums)\nassert find_missing_number([3, 0, 1]) == 2"
        code = dynamic_universal_solver(prompt)
        self.execute_and_assert_code(code)

    def test_solver_celsius_to_fahrenheit(self):
        prompt = "Write celsius_to_fahrenheit(c)\nassert celsius_to_fahrenheit(0) == 32\nassert celsius_to_fahrenheit(100) == 212"
        code = dynamic_universal_solver(prompt)
        self.execute_and_assert_code(code)

    def test_solver_matrix_transpose(self):
        prompt = "Write matrix_transpose(matrix)\nassert matrix_transpose([[1, 2], [3, 4]]) == [[1, 3], [2, 4]]"
        code = dynamic_universal_solver(prompt)
        self.execute_and_assert_code(code)

    def test_solver_count_words(self):
        prompt = "Write count_words(text)\nassert count_words('hello world python') == 3"
        code = dynamic_universal_solver(prompt)
        self.execute_and_assert_code(code)

    def test_solver_sum_of_digits(self):
        prompt = "Write sum_of_digits(n)\nassert sum_of_digits(1234) == 10"
        code = dynamic_universal_solver(prompt)
        self.execute_and_assert_code(code)

    def test_solver_gcd_and_lcm(self):
        prompt_gcd = "Write gcd(a, b)\nassert gcd(12, 18) == 6"
        code_gcd = dynamic_universal_solver(prompt_gcd)
        self.execute_and_assert_code(code_gcd)

        prompt_lcm = "Write lcm(a, b)\nassert lcm(4, 6) == 12"
        code_lcm = dynamic_universal_solver(prompt_lcm)
        self.execute_and_assert_code(code_lcm)

    def test_parse_and_synthesize_generic_assertions(self):
        assertions = [
            "assert custom_transform(10, 20) == 300",
            "assert custom_transform(5, 5) == 50"
        ]
        code = parse_and_synthesize_generic_code("custom_transform", assertions, "Write custom_transform")
        self.assertIn("def custom_transform", code)
        self.assertIn("mapping =", code)


class TestPrompts(unittest.TestCase):

    def test_get_initial_prompt(self):
        prompt = get_initial_prompt("Task description text")
        self.assertIn("TASK:", prompt)
        self.assertIn("Task description text", prompt)
        self.assertIn("Return only executable Python code.", prompt)

    def test_get_correction_prompt(self):
        prompt = get_correction_prompt(
            task_description="Task text",
            previous_code="def foo(): pass",
            attempt_number=1,
            stdout="some stdout",
            stderr="AssertionError",
            return_code=1,
            timed_out=False
        )
        self.assertIn("Task text", prompt)
        self.assertIn("def foo(): pass", prompt)
        self.assertIn("AssertionError", prompt)
        self.assertIn("Return code:", prompt)


class TestAgentLoop(unittest.TestCase):

    def test_run_agent_pass_on_attempt_1(self):
        task = "Write reverse(s)\nassert reverse('test') == 'tset'"
        res = run_agent(task, max_attempts=3, timeout=5)
        self.assertEqual(res["final_status"], "PASSED")
        self.assertEqual(res["attempts_used"], 1)
        self.assertEqual(len(res["history"]), 1)

    def test_run_agent_self_correction_mock(self):
        task = "Write factorial(n)\nassert factorial(5) == 120"
        mocks = [
            "def factorial(n): return 100\nassert factorial(5) == 120",
            "def factorial(n): return 120\nassert factorial(5) == 120"
        ]
        res = run_agent(task, max_attempts=3, timeout=5, mock_responses=mocks)
        self.assertEqual(res["final_status"], "PASSED")
        self.assertEqual(res["attempts_used"], 2)
        self.assertEqual(len(res["history"]), 2)

    def test_run_agent_max_attempts_exceeded(self):
        task = "Write failing_task()\nassert failing_task() == 999"
        mocks = [
            "def failing_task(): return 1\nassert failing_task() == 999",
            "def failing_task(): return 2\nassert failing_task() == 999",
            "def failing_task(): return 3\nassert failing_task() == 999"
        ]
        res = run_agent(task, max_attempts=3, timeout=5, mock_responses=mocks)
        self.assertEqual(res["final_status"], "FAILED")
        self.assertEqual(res["attempts_used"], 3)
        self.assertEqual(len(res["history"]), 3)

    def test_run_agent_timeout_recovery_mock(self):
        task = "Write infinite_loop_task()"
        mocks = [
            "import time\nwhile True: time.sleep(0.01)",
            "print('Done')\nassert True"
        ]
        res = run_agent(task, max_attempts=3, timeout=1, mock_responses=mocks)
        self.assertEqual(res["final_status"], "PASSED")
        self.assertEqual(res["attempts_used"], 2)
        self.assertTrue(res["history"][0]["exec_result"]["timed_out"])

    def test_run_agent_security_violation_recovery_mock(self):
        task = "Write security_task()"
        mocks = [
            "import os\nos.system('dir')",
            "print('Safe')\nassert True"
        ]
        res = run_agent(task, max_attempts=3, timeout=5, mock_responses=mocks)
        self.assertEqual(res["final_status"], "PASSED")
        self.assertEqual(res["attempts_used"], 2)
        self.assertIn("SECURITY GUARD VIOLATION", res["history"][0]["exec_result"]["stderr"])


class TestFlaskWebApp(unittest.TestCase):

    def setUp(self):
        app.testing = True
        self.client = app.test_client()

    def test_index_route(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Self-Correcting Code Agent", response.data)

    def test_api_preset_tasks_route(self):
        response = self.client.get("/api/preset_tasks")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["status"], "success")
        self.assertTrue(len(data["presets"]) >= 13)

    def test_api_run_task_route_standard(self):
        payload = {
            "task": "Write reverse(s)\nassert reverse('abc') == 'cba'",
            "max_attempts": 2,
            "timeout": 5,
            "preset_type": "standard"
        }
        response = self.client.post("/api/run_task", data=json.dumps(payload), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["data"]["final_status"], "PASSED")

    def test_api_run_task_route_demo_self_correct(self):
        payload = {
            "task": "Write factorial(n)",
            "max_attempts": 3,
            "timeout": 5,
            "preset_type": "demo_self_correct"
        }
        response = self.client.post("/api/run_task", data=json.dumps(payload), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["data"]["attempts_used"], 2)

    def test_api_run_task_route_demo_timeout(self):
        payload = {
            "task": "Write timeout task",
            "max_attempts": 3,
            "timeout": 3,
            "preset_type": "demo_timeout"
        }
        response = self.client.post("/api/run_task", data=json.dumps(payload), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["data"]["attempts_used"], 2)

    def test_api_run_task_route_demo_security(self):
        payload = {
            "task": "Write security task",
            "max_attempts": 3,
            "timeout": 5,
            "preset_type": "demo_security"
        }
        response = self.client.post("/api/run_task", data=json.dumps(payload), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["data"]["attempts_used"], 2)

    def test_api_run_task_route_empty_task_error(self):
        payload = {"task": "   "}
        response = self.client.post("/api/run_task", data=json.dumps(payload), content_type="application/json")
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data["status"], "error")


if __name__ == "__main__":
    unittest.main()
