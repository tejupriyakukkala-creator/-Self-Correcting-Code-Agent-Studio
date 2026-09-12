"""
Prompt templates for code generation and self-correction.
"""

SYSTEM_PROMPT = """You are an expert Python developer and automated coding assistant.
Your goal is to write clean, correct, and self-contained Python code that satisfies all given task requirements and passes all test assertions.
Return ONLY executable Python code. Do not include markdown code block fences (like ```python) and do not include explanations or introductory text."""


def get_initial_prompt(task_description: str) -> str:
    """
    Constructs the initial prompt for first-attempt code generation.
    """
    return f"""Generate Python code that solves the following task.

TASK:
{task_description}

Return only executable Python code.
Do not include Markdown fences or explanations.
The code must include the required assertions/tests."""


def get_correction_prompt(
    task_description: str,
    previous_code: str,
    attempt_number: int,
    stdout: str,
    stderr: str,
    return_code: int,
    timed_out: bool,
) -> str:
    """
    Constructs the feedback prompt when code execution fails, asking the LLM to fix the solution.
    """
    return f"""You are debugging a Python solution.

Original task:
{task_description}

Previous code (Attempt {attempt_number}):
{previous_code}

Execution result:
stdout:
{stdout if stdout else "(No stdout output)"}

stderr:
{stderr if stderr else "(No stderr output)"}

Return code:
{return_code}

Timed out:
{timed_out}

The program failed.

Identify the problem and return a complete corrected Python solution.

Requirements:
- Preserve the original task requirements.
- Make all assertions pass.
- Return only executable Python code.
- Do not include Markdown fences.
- Do not include explanations."""
