from .models import Problem, TestCase
from rest_framework import status
from .RunCode import execute_code_with_callback
from django.core.cache import cache
import time

def run_code(problem_id, code, language):
    try:
        problem = Problem.objects.get(pk=problem_id)
    except Problem.DoesNotExist:
        return {"error": "Problem not found", "status": status.HTTP_404_NOT_FOUND}

    # Retrieve and transform test cases
    test_cases_queryset = TestCase.objects.filter(problem=problem)
    test_cases = [
        {
            "input": test_case.input_data,
            "expected_output": test_case.expected_output
        }
        for test_case in test_cases_queryset
    ]

    # Use the execute_code_with_callback function
    callback_url = "http://192.168.137.1:8000/judge0/callback/"  # Replace with the appropriate URL
    execute_code_with_callback(language, code, problem.class_name, problem.method_name, test_cases, problem_id, callback_url)
    
    # Prepare to wait for the callback result
    cache_key_result = f"judge0_result"
    cache_key_flag = f"judge0_flag"
    cache.set(cache_key_flag, False, timeout=300)  # Initialize the flag in the cache

    # Wait for the callback
    timeout = 30  # Timeout in seconds
    polling_interval = 0.5  # Polling interval in seconds
    elapsed_time = 0
    result = None

    while elapsed_time < timeout:
        flag = cache.get(cache_key_flag)
        if flag:  # Check if the flag is set by the callback
            result = cache.get(cache_key_result)
            break
        time.sleep(polling_interval)
        elapsed_time += polling_interval
    
    # Clean up
    cache.delete(cache_key_flag)
    cache.delete(cache_key_result)

    if result:
        return {"message": "Execution completed", "result": result, "status": status.HTTP_200_OK}
    else:
        return {"message": "Execution timed out", "status": status.HTTP_504_GATEWAY_TIMEOUT}
