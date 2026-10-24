import sys
import subprocess
import time
import re
import tempfile
import os

DISALLOWED_PATTERNS = [
    r"\bimport\s+subprocess\b",
    r"\bfrom\s+subprocess\b",
    r"\bimport\s+shutil\b",
    r"\bshutil\.rmtree\b",
    r"\bos\.system\b",
    r"\bos\.remove\b",
    r"\bos\.unlink\b",
    r"\bos\.rmdir\b",
    r"\bimport\s+socket\b",
    r"\bimport\s+urllib\b",
    r"\bimport\s+requests\b",
    r"\bimport\s+http\b",
    r"\bimport\s+ctypes\b",
    r"\b__import__\(['\"]subprocess['\"]\)",
    r"\b__import__\(['\"]os['\"]\)\.system",
    r"\b__import__\(['\"]socket['\"]\)",
]

def check_code_safety(code: str) -> tuple[bool, str]:
    """Basic security check to block hazardous operations in code."""
    for pattern in DISALLOWED_PATTERNS:
        if re.search(pattern, code, re.IGNORECASE):
            return False, f"Security Violation: Restricted module or call detected ({pattern})"
    return True, ""

def execute_single_case(code: str, test_input: str, expected_output: str, timeout_sec: float = 3.0) -> dict:
    """Executes code with given stdin and compares stdout with expected_output."""
    safe, reason = check_code_safety(code)
    if not safe:
        return {
            "passed": False,
            "status": "Security Error",
            "error": reason,
            "stdout": "",
            "expected": expected_output,
            "runtime_ms": 0
        }

    # Write code to a temporary file
    temp_dir = tempfile.gettempdir()
    temp_file = os.path.join(temp_dir, f"sol_{os.getpid()}_{time.time_ns()}.py")

    with open(temp_file, "w", encoding="utf-8") as f:
        f.write(code)

    start_time = time.time()
    try:
        proc = subprocess.Popen(
            [sys.executable, "-I", temp_file],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace"
        )
        try:
            stdout_data, stderr_data = proc.communicate(input=test_input or "", timeout=timeout_sec)
            elapsed_ms = round((time.time() - start_time) * 1000, 2)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.communicate()
            return {
                "passed": False,
                "status": "Time Limit Exceeded",
                "error": f"Execution exceeded {timeout_sec} seconds limit.",
                "stdout": "",
                "expected": expected_output,
                "runtime_ms": round(timeout_sec * 1000, 2)
            }

        # Normalize stdout and expected
        norm_actual = "\n".join(line.rstrip() for line in stdout_data.strip().splitlines())
        norm_expected = "\n".join(line.rstrip() for line in (expected_output or "").strip().splitlines())

        if proc.returncode != 0:
            return {
                "passed": False,
                "status": "Runtime Error",
                "error": stderr_data.strip(),
                "stdout": stdout_data.strip(),
                "expected": expected_output,
                "runtime_ms": elapsed_ms
            }

        passed = (norm_actual == norm_expected)
        return {
            "passed": passed,
            "status": "Passed" if passed else "Wrong Answer",
            "stdout": norm_actual,
            "expected": norm_expected,
            "error": "",
            "runtime_ms": elapsed_ms
        }

    except Exception as e:
        return {
            "passed": False,
            "status": "System Error",
            "error": str(e),
            "stdout": "",
            "expected": expected_output,
            "runtime_ms": 0
        }
    finally:
        if os.path.exists(temp_file):
            try:
                os.remove(temp_file)
            except Exception:
                pass

def run_all_test_cases(code: str, test_cases: list[dict], run_hidden: bool = True) -> dict:
    """Runs code through a list of test cases."""
    results = []
    total_count = 0
    passed_count = 0

    for i, tc in enumerate(test_cases):
        is_hidden = tc.get("is_hidden", False)
        if is_hidden and not run_hidden:
            continue
            
        total_count += 1
        test_in = tc.get("input", "")
        # Automatically normalize escaped newlines like '\n' if present as literal string
        if isinstance(test_in, str) and "\\n" in test_in and "\n" not in test_in:
            test_in = test_in.replace("\\n", "\n")
            
        test_exp = tc.get("expected_output", "")
        if isinstance(test_exp, str) and "\\n" in test_exp and "\n" not in test_exp:
            test_exp = test_exp.replace("\\n", "\n")
        
        res = execute_single_case(code, test_in, test_exp)
        res["case_number"] = i + 1
        res["is_hidden"] = is_hidden
        
        # If it's a hidden test case and failed, mask exact input/expected for anti-cheat
        if is_hidden and not res["passed"]:
            res_report = {
                "case_number": i + 1,
                "is_hidden": True,
                "passed": False,
                "status": res["status"],
                "runtime_ms": res["runtime_ms"],
                "error": res["error"] if res["status"] in ["Runtime Error", "Security Error", "Time Limit Exceeded"] else "",
                "stdout": "[Hidden Test Case]",
                "expected": "[Hidden Test Case]"
            }
        else:
            res_report = {
                "case_number": i + 1,
                "is_hidden": is_hidden,
                "passed": res["passed"],
                "status": res["status"],
                "runtime_ms": res["runtime_ms"],
                "error": res["error"],
                "stdout": res["stdout"],
                "expected": res["expected"]
            }

        if res["passed"]:
            passed_count += 1
            
        results.append(res_report)

    all_passed = (passed_count == total_count and total_count > 0)
    score_ratio = (passed_count / total_count) if total_count > 0 else 0.0

    return {
        "all_passed": all_passed,
        "total": total_count,
        "passed": passed_count,
        "score_ratio": score_ratio,
        "results": results
    }
