from .models import Problem, TestCase
from rest_framework import status
from .RunCode import execute_code_submission


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

    # Execute the code (tries Judge0 first, falls back to local execution)
    result = execute_code_submission(
        language, code, problem.class_name, problem.method_name,
        test_cases, problem_id
    )

    if result:
        return {"message": "Execution completed", "result": result, "status": status.HTTP_200_OK}
    else:
        return {"message": "Execution timed out", "status": status.HTTP_504_GATEWAY_TIMEOUT}
