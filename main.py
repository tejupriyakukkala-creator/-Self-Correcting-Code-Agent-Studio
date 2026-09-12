"""
Main entry point for running the safe autonomous self-correcting agent.
Runs the 5 primary programming tasks, the self-correction demo, and the timeout safety demo.
"""

import sys
import os

# Add project root directory to path to enable package execution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from self_correcting_agent.agent import run_agent
from self_correcting_agent.tests import TASKS, DEMO_SELF_CORRECT_TASK, DEMO_TIMEOUT_TASK, DEMO_SECURITY_TASK


def print_summary_table(results):
    """
    Renders a formatted ASCII summary table of all executed tasks.
    """
    header = f"+--------------------------------------------+----------+--------+"
    title  = f"| Task                                       | Attempts | Result |"
    print("\n" + "=" * 66)
    print("FINAL DEMONSTRATION SUMMARY")
    print("=" * 66)
    print(header)
    print(title)
    print(header)
    for r in results:
        task_name = (r['task_name'][:42]).ljust(42)
        attempts  = str(r['attempts']).center(8)
        result    = r['result'].center(6)
        print(f"| {task_name} | {attempts} | {result} |")
    print(header)
    print("\n")


def main():
    print("\n" + "#" * 70)
    print("  SAFE AUTONOMOUS CODE-GENERATION AGENT")
    print("  Loop: Generate -> Execute -> Observe -> Evaluate -> Self-Correct -> Retry")
    print("#" * 70)

    summary_results = []

    # Part 1: Run standard programming tasks
    print("\n\n>>> PART 1: RUNNING STANDARD PROGRAMMING TASKS <<<\n")
    for t in TASKS:
        res = run_agent(t["task"], max_attempts=3, timeout=10)
        summary_results.append({
            "task_name": t["name"],
            "attempts": res["attempts_used"],
            "result": res["final_status"]
        })

    # Part 2: Demonstrate explicit Self-Correction
    print("\n\n>>> PART 2: DEMONSTRATING EXPLICIT SELF-CORRECTION (Attempt 1 Bug -> Attempt 2 Fix) <<<\n")
    res_sc = run_agent(
        DEMO_SELF_CORRECT_TASK["task"],
        max_attempts=3,
        timeout=10,
        mock_responses=DEMO_SELF_CORRECT_TASK["mock_responses"]
    )
    summary_results.append({
        "task_name": DEMO_SELF_CORRECT_TASK["name"],
        "attempts": res_sc["attempts_used"],
        "result": res_sc["final_status"]
    })

    # Part 3: Demonstrate Subprocess Timeout Safety
    print("\n\n>>> PART 3: DEMONSTRATING SUBPROCESS TIMEOUT SAFETY (Infinite Loop Catch) <<<\n")
    res_to = run_agent(
        DEMO_TIMEOUT_TASK["task"],
        max_attempts=3,
        timeout=3,  # Short 3-second timeout for quick demo
        mock_responses=DEMO_TIMEOUT_TASK["mock_responses"]
    )
    summary_results.append({
        "task_name": DEMO_TIMEOUT_TASK["name"],
        "attempts": res_to["attempts_used"],
        "result": res_to["final_status"]
    })

    # Part 4: Demonstrate AST Security Guard Block
    print("\n\n>>> PART 4: DEMONSTRATING AST SECURITY GUARD BLOCK <<<\n")
    res_sec = run_agent(
        DEMO_SECURITY_TASK["task"],
        max_attempts=3,
        timeout=10,
        mock_responses=DEMO_SECURITY_TASK["mock_responses"]
    )
    summary_results.append({
        "task_name": DEMO_SECURITY_TASK["name"],
        "attempts": res_sec["attempts_used"],
        "result": res_sec["final_status"]
    })

    # Part 5: Display Summary Table
    print_summary_table(summary_results)


if __name__ == "__main__":
    main()
