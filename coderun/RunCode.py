import requests
import base64
from .models import Problem

JUDGE0_API_URL = "http://localhost:2358"
LANGUAGE_MAP = {
    "python": 71,  
    "cpp": 54,     
    "java": 62,   
}


def generate_driver_script(language, user_code, method_name, test_cases, problem_id):
    problem = Problem.objects.get(id=problem_id)
    driver_template = problem.driver_template

    if language == "cpp":
        formatted_test_cases = ",\n".join(
            f"{{ {{ {', '.join(map(str, test_case['input']['nums']))} }}, {test_case['input']['target']} }}"
            for test_case in test_cases
        )
        formatted_expected_outputs = ",\n".join(
            f"{{{', '.join(map(str, test_case['expected_output']))}}}" for test_case in test_cases
        )
        driver_code = driver_template[language].format(
            user_code=user_code,
            method_name=method_name,
            test_cases=formatted_test_cases,
            expected_outputs=formatted_expected_outputs,
            class_name=problem.class_name,
        )
    else:
        formatted_test_cases = "\n".join(
            [f"{{'input': {test_case['input']}, 'expected_output': {test_case['expected_output']}}}," for test_case in test_cases]
        )
        driver_code = driver_template[language].format(
            user_code=user_code,
            method_name=method_name,
            test_cases=formatted_test_cases,
            class_name=problem.class_name,
        )
        print(driver_code)
    return driver_code


def execute_code_with_callback(language, user_code, class_name, method_name, test_cases, problem_id, callback_url):
    driver_code = generate_driver_script(language, user_code, method_name, test_cases, problem_id)
    print(driver_code)
    encoded_code = base64.b64encode(driver_code.encode('utf-8')).decode('utf-8')

    data = {
        "language_id": LANGUAGE_MAP[language],
        "source_code": encoded_code,
        "callback_url": callback_url,
    }

    headers = {
        "Content-Type": "application/json",
    }
    

    response = requests.post(f"{JUDGE0_API_URL}/submissions?base64_encoded=true", json=data, headers=headers)
    if response.status_code != 201:
        raise Exception(f"Error submitting code to Judge0: {response.text}")
    
    print(response.json())
    return response.json()
