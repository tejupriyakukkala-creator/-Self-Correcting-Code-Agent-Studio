# Execute, Observe, Self-Correct: Safe Code Generation Agent

An autonomous, self-correcting Python code generation agent that moves beyond simple one-shot code output. Instead of stopping after code generation, this agent safely inspects code via AST security guards, executes untrusted LLM-generated code in an isolated child process, captures execution feedback, evaluates output/error signals, and automatically prompts the LLM to self-correct upon failure.

---

## 1. Overview & Concept

Traditional AI coding tools function as autocomplete systems: they produce a code snippet and stop. If the generated code contains a syntax error, runtime exception, logic bug, or failed assertion, the user must manually copy the error message back to the LLM.

This project implements a complete **Generate → Safety-Check → Execute → Observe → Evaluate → Self-Correct → Retry** loop:

1. **Generate**: Prompt LLM with task requirements and assertion tests.
2. **Safety-Check**: Perform static AST analysis to block dangerous system imports (`os.system`, `shutil`, `socket`, `ctypes`, `eval`, `exec`).
3. **Execute**: Write generated code to a temporary `.py` file and run it inside a separate child subprocess.
4. **Observe**: Capture `stdout`, `stderr`, return codes, and timeout status.
5. **Evaluate**: Determine if the process exited cleanly (`returncode == 0` without timing out or security violation).
6. **Self-Correct**: If execution failed, send the exact error context (tracebacks, assertion failures, timeout state, security violation) back to the LLM.
7. **Retry**: Repeat execution until all tests pass or the maximum attempt limit (**3 attempts**) is reached.

---

## 2. Architecture

```text
               User Task
                   ↓
         Code Generation LLM
                   ↓
         Generated Python Code
                   ↓
        Code Extractor / Cleaner
                   ↓
         AST Static Security Check
                   ↓
          Temporary .py File
                   ↓
       Safe Subprocess Executor
                   ↓
            Execution Result
    ├── stdout
    ├── stderr
    ├── return code
    └── timeout state
                   ↓
            Result Evaluator
                   ↓
                Passed?
        ┌──────────┴──────────┐
       YES                   NO
        ↓                     ↓
     Finish            Error Feedback
                              ↓
                        LLM Fix Prompt
                              ↓
                           New Code
                              ↓
                            Retry (Max 3)
```

---

## 3. Safety & Process Isolation

Executing LLM-generated code presents security risks. This project enforces strict runtime safety guidelines:

### Critical Red Lines
- **No `eval()` or `exec()`**: Code is **NEVER** executed dynamically within the main agent process.
- **No Direct Imports**: Generated modules are **NEVER** imported into the host Python runtime.
- **AST Pre-Execution Guard**: Code is statically analyzed using Python's `ast` module to reject prohibited imports (`shutil`, `ctypes`, `socket`, `os.system`, `eval`, `exec`).

### Safety Boundaries Implemented
1. **AST Static Security Check**: Blocks dangerous modules/builtins before subprocess execution.
2. **Isolated Subprocess Execution**: Code is saved to a temporary file (`tempfile.NamedTemporaryFile`) and executed in a child process via:
   ```python
   subprocess.run(
       [sys.executable, temp_path],
       capture_output=True,
       text=True,
       timeout=10
   )
   ```
3. **Timeout Protection**: The process is capped at a strict duration (e.g., 10 seconds). If generated code enters an infinite loop, `subprocess.TimeoutExpired` is caught, logging `STATUS: TIMEOUT` without hanging the host agent.
4. **Guaranteed Resource Cleanup**: Temporary files are deleted inside `finally` blocks, ensuring no residual files remain on disk regardless of execution success or failure.
5. **Bounded Retry Loop**: The agent enforces a strict `MAX_ATTEMPTS = 3` cap, preventing infinite retry loops.

> [!NOTE]
> **Production Security Note**: `subprocess.run()` with a timeout and AST checking provides demonstration-level process isolation. For production environments handling multi-tenant or untrusted code execution, additional isolation layers such as Docker/container sandboxes, gVisor, rootless environments, network disabling, and resource quotas (cgroups) are required.

---

## 4. Project Structure

```text
self_correcting_agent/
│
├── main.py            # Entry point running standard tasks, demonstrations, and summary table
├── agent.py           # Self-correction loop (run_agent), LLM API handler, and dynamic universal solver
├── executor.py        # Safe code cleaner, AST security check, and subprocess runner
├── prompts.py         # System prompts, initial generation, and error feedback templates
├── tests.py           # 10 primary programming tasks + self-correction, timeout, & security demos
├── test_agent.py      # Automated unit test suite using unittest
├── web_app.py         # Flask REST API web server for interactive browser UI
├── templates/
│   └── index.html     # Modern glassmorphism web UI dashboard
├── requirements.txt   # Dependencies (openai, google-genai, flask, python-dotenv)
└── README.md          # Complete project documentation and execution results
```

---

## 5. Installation & Setup

### Prerequisites
- Python 3.9+ installed.

### Setup Environment
1. Clone or navigate to the project workspace.
2. Install dependencies:
   ```bash
   pip install -r self_correcting_agent/requirements.txt
   ```
3. (Optional) Set up your LLM API key in `.env` or export environment variables:
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   # or export GEMINI_API_KEY="your-gemini-key"
   ```
   *Note: If no API key is configured, the agent seamlessly operates in standalone fallback mode using the dynamic universal solver for testing and demonstration.*

### Execution Options

#### 1. Command Line Execution (Main Demonstration)
Run all 10 core programming tasks and 3 safety/self-correction demos:
```bash
python self_correcting_agent/main.py
```

#### 2. Run Unit Test Suite
Execute the automated test suite covering all modules:
```bash
python -m unittest self_correcting_agent/test_agent.py
```

#### 3. Run Web Dashboard
Launch the interactive web UI dashboard:
```bash
python self_correcting_agent/web_app.py
```
Then open `http://localhost:5000` in your web browser.

---

## 6. Test Suite & Demonstrations

The agent is evaluated on 10 core programming tasks containing executable assertions, followed by explicit self-correction, timeout safety, and security guard demonstrations:

### Core Tasks
1. **Reverse String**: `reverse(s)` reversing input strings.
2. **Palindrome**: `is_palindrome(s)` detecting palindrome strings.
3. **Factorial**: `factorial(n)` computing non-negative integer factorials.
4. **Prime Number**: `is_prime(n)` checking prime numbers.
5. **Fibonacci**: `fibonacci(n)` computing Nth Fibonacci number.
6. **Binary Search**: `binary_search(arr, target)` searching sorted arrays.
7. **Frequency Counter**: `count_frequency(items)` counting occurrences in lists.
8. **Two Sum**: `two_sum(nums, target)` finding indices summing to target.
9. **Valid Parentheses**: `is_valid_parentheses(s)` validating bracket matching.
10. **Flatten List**: `flatten_list(nested_list)` flattening nested lists.

### Special Demonstrations
- **Self-Correction Demo**: Simulates an intentional `AssertionError` on Attempt 1 (`factorial(5) == 100`), observes the traceback, constructs an error feedback prompt, and verifies that Attempt 2 passes.
- **Timeout Safety Demo**: Executes an infinite loop (`while True: pass`), observes the `subprocess.TimeoutExpired` signal after 3 seconds, logs `STATUS: TIMEOUT`, and retries safely.
- **AST Security Guard Demo**: Rejects prohibited system call `os.system("echo Hacked")` at AST analysis phase before execution, feeding security violation notice back to LLM to self-correct safely.

---

## 7. Execution Logs & Results

### Final Summary Table

```text
==================================================================
FINAL DEMONSTRATION SUMMARY
==================================================================
+--------------------------------------------+----------+--------+
| Task                                       | Attempts | Result |
+--------------------------------------------+----------+--------+
| Reverse String                             |    1     | PASSED |
| Palindrome                                 |    1     | PASSED |
| Factorial                                  |    1     | PASSED |
| Prime Number                               |    1     | PASSED |
| Fibonacci                                  |    1     | PASSED |
| Binary Search                              |    1     | PASSED |
| Frequency Counter                          |    1     | PASSED |
| Two Sum                                    |    1     | PASSED |
| Valid Parentheses                          |    1     | PASSED |
| Flatten Nested List                        |    1     | PASSED |
| Factorial (Forced Failure & Self-Correctio |    2     | PASSED |
| Infinite Loop Safety Demo                  |    2     | PASSED |
| Security Guard Block Demo                  |    2     | PASSED |
+--------------------------------------------+----------+--------+
```

---

## 8. Key Takeaway

By combining AST static security analysis, isolated subprocess execution, runtime metric capture, and automated feedback loops, the system operates as an **autonomous agent** capable of independent problem-solving, self-correction, and secure execution.
