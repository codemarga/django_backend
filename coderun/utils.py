from .models import Problem, TestCase
from rest_framework import status
from .RunCode import execute_code_with_callback
from django.core.cache import cache
from threading import Event
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
    callback_url = "http://localhost:8000/judge0/callback/"  # Replace with the appropriate URL
    execute_code_with_callback(language, code, problem.class_name, problem.method_name, test_cases, problem_id, callback_url)
    
    # Prepare to wait for the callback result
    cache_key_result = f"judge0_result_{problem_id}"
    cache_key_event = f"judge0_event_{problem_id}"
    event = Event()
    cache.set(cache_key_event, event, timeout=300)  # Store the event for synchronization

    # Wait for the callback
    result = None
    if event.wait(timeout=30):  # Wait up to 30 seconds for the callback
        result = cache.get(cache_key_result)
    
    # Clean up
    cache.delete(cache_key_event)
    cache.delete(cache_key_result)

    if result:
        return {"message": "Execution completed", "result": result, "status": status.HTTP_200_OK}
    else:
        return {"message": "Execution timed out", "status": status.HTTP_504_GATEWAY_TIMEOUT}
