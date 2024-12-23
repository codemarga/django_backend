from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from .models import Problem , TestCase
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import json


# View to display all problems
class ProblemListView(APIView):
    def get(self, request):
        problems = Problem.objects.all()
        problem_list = [
            {
                "id": problem.id,
                "title": problem.title,
                "description": problem.description,
            }
            for problem in problems
        ]
        return JsonResponse(problem_list, safe=False, status=200)


# View to display all details of a specific problem
class ProblemDetailView(APIView):
    def get(self, request, pk):
        try:
            problem = Problem.objects.get(pk=pk)
            problem_details = {
                "id": problem.id,
                "title": problem.title,
                "description": problem.description,
                "examples": problem.examples,
                "constraints": problem.constraints,
                "default_code": problem.default_code,
                "class_name": problem.class_name,
                "method_name": problem.method_name,
                "followup": problem.followup,
                "category": problem.category.name if problem.category else None,
            }
            return JsonResponse(problem_details, status=200)
        except ObjectDoesNotExist:
            return JsonResponse({"error": "Problem not found"}, status=404)
        
        

"""
class RunCodeView(APIView):
    def post(self, request):
        try:
            problem_id = request.data.get("problem_id")
            code = request.data.get("code")
            language = request.data.get("language")
            print(problem_id, code, language)

            if not problem_id or not code or not language:
                return Response({"error": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST)

            try:
                problem = Problem.objects.get(pk=problem_id)
            except Problem.DoesNotExist:
                return Response({"error": "Problem not found"}, status=status.HTTP_404_NOT_FOUND)

            # Retrieve and transform test cases
            test_cases_queryset = TestCase.objects.filter(problem=problem)
            test_cases = []

            for test_case in test_cases_queryset:
                
                # Assuming input_data is stored as a JSON string in the database
                print(test_case.input_data)
                test_cases.append({
                    "input": test_case.input_data,
                    "expected_output": test_case.expected_output
                })
                print(test_cases)
                

            print(test_cases)

            output = execute_code(language, code, problem.class_name, problem.method_name, test_cases, problem_id)

            return Response(output, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

"""


from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .RunCode import execute_code_with_callback


class RunCodeView(APIView):
    def post(self, request):
        try:
            problem_id = request.data.get("problem_id")
            code = request.data.get("code")
            language = request.data.get("language")

            if not problem_id or not code or not language:
                return Response({"error": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST)

            try:
                problem = Problem.objects.get(pk=problem_id)
            except Problem.DoesNotExist:
                return Response({"error": "Problem not found"}, status=status.HTTP_404_NOT_FOUND)

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
            callback_url = "http://172.20.10.13:8000/judge0/callback/"
            print(callback_url)
            execute_code_with_callback(language, code, problem.class_name, problem.method_name, test_cases, problem_id, callback_url)
            print("Code submitted for execution")
            return Response({"message": "Code submitted for execution"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@method_decorator(csrf_exempt, name='dispatch')
class Judge0CallbackView(APIView):
    def put(self, request):
        try:
            print("Callback received")
            data = json.loads(request.body)
            # Process Judge0 callback data (save results, update submission status, etc.)
            print("Callback received:", data)
            return Response({"message": "Callback processed successfully"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

