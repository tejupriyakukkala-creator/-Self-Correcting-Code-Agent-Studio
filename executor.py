"""
Executor module responsible for cleaning LLM responses and safely executing Python code
in isolated child subprocesses using temporary files and execution timeouts.
"""

import os
import re
import sys
import tempfile
import subprocess
from typing import Dict, Any, Optional


def clean_code(response: str) -> str:
    """
    Extracts raw Python code from LLM responses by stripping Markdown code fences
    and extra whitespace.
    """
    if not response:
        return ""

    # Check for Markdown code fence blocks (```python ... ``` or ``` ... ```)
    pattern = r"```(?:python)?\s*\n?(.*?)\n?```"
    matches = re.findall(pattern, response, re.DOTALL | re.IGNORECASE)
    
    if matches:
        # Join extracted code blocks if multiple exist, or take the main one
        cleaned = "\n\n".join(match.strip() for match in matches)
    else:
        # If no triple backticks found, strip single backticks or leading/trailing text if needed
        cleaned = response.strip()
        if cleaned.startswith("```python"):
            cleaned = cleaned[9:]
        elif cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]

    return cleaned.strip()


import ast

DISALLOWED_IMPORTS = {"os.system", "shutil", "ctypes", "subprocess", "socket", "urllib", "requests", "http"}
DISALLOWED_BUILTINS = {"eval", "exec", "__import__", "compile", "globals", "locals"}


def check_code_safety(code: str) -> Optional[str]:
    """
    Performs AST static analysis to inspect code for prohibited security patterns
    such as system execution, raw socket opening, or dynamic compilation calls.
    Returns None if safe, or an error message string if a security violation is found.
    """
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        # Let execution catch syntax errors at runtime
        return None

    for node in ast.walk(tree):
        # Check imports (import os, import shutil, etc.)
        if isinstance(node, ast.Import):
            for alias in node.names:
                name = alias.name.split('.')[0]
                if name in {"shutil", "ctypes", "socket"}:
                    return f"Security Violation: Import of '{alias.name}' is prohibited."

        # Check from ... import ...
        elif isinstance(node, ast.ImportFrom):
            if node.module and node.module.split('.')[0] in {"shutil", "ctypes", "socket"}:
                return f"Security Violation: Import from '{node.module}' is prohibited."

        # Check call expressions like eval(), exec(), __import__()
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                if node.func.id in DISALLOWED_BUILTINS:
                    return f"Security Violation: Function '{node.func.id}()' is prohibited."
            elif isinstance(node.func, ast.Attribute):
                # e.g., os.system(...)
                if isinstance(node.func.value, ast.Name):
                    call_path = f"{node.func.value.id}.{node.func.attr}"
                    if call_path in DISALLOWED_IMPORTS:
                        return f"Security Violation: Method '{call_path}()' is prohibited."

    return None


def execute_code(code: str, timeout: int = 10) -> Dict[str, Any]:
    """
    Safely executes the provided Python code in an isolated child subprocess.
    
    NEVER uses eval() or exec().
    Performs pre-execution AST security verification, writes code to a temporary file,
    invokes sys.executable in a subprocess, captures stdout/stderr, handles timeout,
    and guarantees temp file deletion.

    Args:
        code: Python source code to execute.
        timeout: Maximum execution duration in seconds (default: 10s).

    Returns:
        Structured result dict containing:
        - passed (bool)
        - stdout (str)
        - stderr (str)
        - return_code (int or None)
        - timed_out (bool)
    """
    # 0. AST Static Security Pre-Check
    safety_error = check_code_safety(code)
    if safety_error:
        return {
            "passed": False,
            "stdout": "",
            "stderr": f"SECURITY GUARD VIOLATION:\n{safety_error}",
            "return_code": -1,
            "timed_out": False
        }

    temp_path = None
    try:
        # 1. Create a temporary Python file
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".py",
            delete=False,
            encoding="utf-8"
        ) as f:
            f.write(code)
            temp_path = f.name

        # 2. Execute temporary file via subprocess.run() in isolated child process
        completed = subprocess.run(
            [sys.executable, temp_path],
            capture_output=True,
            text=True,
            timeout=timeout
        )

        stdout = completed.stdout.strip() if completed.stdout else ""
        stderr = completed.stderr.strip() if completed.stderr else ""
        return_code = completed.returncode
        passed = (return_code == 0)

        return {
            "passed": passed,
            "stdout": stdout,
            "stderr": stderr,
            "return_code": return_code,
            "timed_out": False
        }

    except subprocess.TimeoutExpired as e:
        stdout = e.stdout.decode("utf-8").strip() if isinstance(e.stdout, bytes) else (e.stdout or "").strip()
        stderr = f"Execution timed out after {timeout} seconds"
        return {
            "passed": False,
            "stdout": stdout,
            "stderr": stderr,
            "return_code": None,
            "timed_out": True
        }

    except Exception as e:
        return {
            "passed": False,
            "stdout": "",
            "stderr": f"Execution error: {str(e)}",
            "return_code": -1,
            "timed_out": False
        }

    finally:
        # 3. Always clean up temporary file
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except OSError:
                pass
