import subprocess
import sys
import os
import time
import base64
import tempfile
import requests
from .models import Problem

JUDGE0_API_URL = os.environ.get("JUDGE0_API_URL", "http://localhost:2358")
LANGUAGE_MAP = {
    "python": 71,  
    "cpp": 54,     
    "java": 62,   
}

DEFAULT_TEMPLATES = {
    "python": """from typing import List, Dict, Tuple, Set, Optional

{user_code}

instance = {class_name}()

test_cases = [
{test_cases}
]

def run_test(inp):
    if isinstance(inp, dict):
        try:
            return instance.{method_name}(**inp)
        except TypeError:
            return instance.{method_name}(*inp.values())
    elif isinstance(inp, (list, tuple)):
        return instance.{method_name}(*inp)
    else:
        return instance.{method_name}(inp)

for test in test_cases:
    try:
        res = run_test(test['input'])
        print(repr(res))
    except Exception as e:
        print(f"ERROR: {e}")
""",
    "cpp": """#include <iostream>
#include <vector>
#include <string>
#include <unordered_map>
#include <algorithm>
using namespace std;

{user_code}

int main() {
    {class_name} instance;
    return 0;
}
""",
    "java": """import java.util.*;

{user_code}

public class Main {
    public static void main(String[] args) {
        {class_name} instance = new {class_name}();
    }
}
"""
}


def generate_driver_script(language, user_code, method_name, test_cases, problem_id):
    try:
        problem = Problem.objects.get(id=problem_id)
        driver_template = problem.driver_template or {}
        class_name = problem.class_name or "Solution"
        method_name = problem.method_name or method_name
    except Problem.DoesNotExist:
        driver_template = {}
        class_name = "Solution"

    template = driver_template.get(language) or DEFAULT_TEMPLATES.get(language, DEFAULT_TEMPLATES["python"])

    formatted_test_cases = "\n".join(
        [f"    {{'input': {repr(test_case['input'])}, 'expected_output': {repr(test_case['expected_output'])}}}," for test_case in test_cases]
    )

    driver_code = template
    driver_code = driver_code.replace("{user_code}", user_code)
    driver_code = driver_code.replace("{class_name}", class_name)
    driver_code = driver_code.replace("{method_name}", method_name)
    driver_code = driver_code.replace("{test_cases}", formatted_test_cases)

    return driver_code


def execute_local(language, driver_code):
    start_time = time.perf_counter()
    stdout_str = ""
    stderr_str = ""
    compile_str = ""
    status_id = 3
    status_desc = "Accepted"

    try:
        if language == "python":
            proc = subprocess.run(
                [sys.executable, "-c", driver_code],
                capture_output=True,
                text=True,
                timeout=10
            )
            elapsed = time.perf_counter() - start_time
            stdout_str = proc.stdout or ""
            stderr_str = proc.stderr or ""
            if proc.returncode != 0:
                status_id = 11
                status_desc = "Runtime Error (NZEC)"
            else:
                status_id = 3
                status_desc = "Accepted"
        elif language == "cpp":
            with tempfile.TemporaryDirectory() as temp_dir:
                src_path = os.path.join(temp_dir, "solution.cpp")
                exe_name = "solution.exe" if sys.platform.startswith("win") else "solution"
                exe_path = os.path.join(temp_dir, exe_name)
                with open(src_path, "w", encoding="utf-8") as f:
                    f.write(driver_code)
                
                compile_proc = subprocess.run(
                    ["g++", "-O2", src_path, "-o", exe_path],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if compile_proc.returncode != 0:
                    status_id = 6
                    status_desc = "Compilation Error"
                    compile_str = compile_proc.stderr or ""
                    elapsed = time.perf_counter() - start_time
                else:
                    run_proc = subprocess.run(
                        [exe_path],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    elapsed = time.perf_counter() - start_time
                    stdout_str = run_proc.stdout or ""
                    stderr_str = run_proc.stderr or ""
                    if run_proc.returncode != 0:
                        status_id = 11
                        status_desc = "Runtime Error (NZEC)"
                    else:
                        status_id = 3
                        status_desc = "Accepted"
        elif language == "java":
            with tempfile.TemporaryDirectory() as temp_dir:
                src_path = os.path.join(temp_dir, "Main.java")
                with open(src_path, "w", encoding="utf-8") as f:
                    f.write(driver_code)
                
                compile_proc = subprocess.run(
                    ["javac", src_path],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if compile_proc.returncode != 0:
                    status_id = 6
                    status_desc = "Compilation Error"
                    compile_str = compile_proc.stderr or ""
                    elapsed = time.perf_counter() - start_time
                else:
                    run_proc = subprocess.run(
                        ["java", "-cp", temp_dir, "Main"],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    elapsed = time.perf_counter() - start_time
                    stdout_str = run_proc.stdout or ""
                    stderr_str = run_proc.stderr or ""
                    if run_proc.returncode != 0:
                        status_id = 11
                        status_desc = "Runtime Error (NZEC)"
                    else:
                        status_id = 3
                        status_desc = "Accepted"
        else:
            elapsed = time.perf_counter() - start_time
            stderr_str = f"Unsupported language: {language}"
            status_id = 13
            status_desc = "Internal Error"

    except subprocess.TimeoutExpired:
        elapsed = time.perf_counter() - start_time
        status_id = 5
        status_desc = "Time Limit Exceeded"
        stderr_str = "Execution timed out (5s limit)."
    except Exception as e:
        elapsed = time.perf_counter() - start_time
        status_id = 13
        status_desc = "Internal Error"
        stderr_str = str(e)

    stdout_b64 = base64.b64encode(stdout_str.encode("utf-8")).decode("utf-8") if stdout_str else None
    stderr_b64 = base64.b64encode(stderr_str.encode("utf-8")).decode("utf-8") if stderr_str else None
    compile_b64 = base64.b64encode(compile_str.encode("utf-8")).decode("utf-8") if compile_str else None

    return {
        "stdout": stdout_b64,
        "stderr": stderr_b64,
        "compile_output": compile_b64,
        "status": {
            "id": status_id,
            "description": status_desc
        },
        "time": str(round(elapsed, 3)),
        "memory": 2048,
    }


def execute_code_submission(language, user_code, class_name, method_name, test_cases, problem_id):
    driver_code = generate_driver_script(language, user_code, method_name, test_cases, problem_id)
    
    # Try Judge0 if running
    lang_id = LANGUAGE_MAP.get(language, 71)
    encoded_code = base64.b64encode(driver_code.encode('utf-8')).decode('utf-8')
    data = {
        "language_id": lang_id,
        "source_code": encoded_code,
    }
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(
            f"{JUDGE0_API_URL}/submissions?base64_encoded=true&wait=true",
            json=data,
            headers=headers,
            timeout=2
        )
        if response.status_code in (200, 201):
            res_json = response.json()
            if "status" in res_json:
                return res_json
    except Exception:
        pass

    # Fallback to direct local execution
    return execute_local(language, driver_code)
