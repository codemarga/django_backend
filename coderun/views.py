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
from .utils import run_code

class RunCodeView(APIView):
    def post(self, request):
        problem_id = request.data.get("problem_id")
        code = request.data.get("code")
        language = request.data.get("language")

        if not problem_id or not code or not language:
            return Response({"error": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST)

        result = run_code(problem_id, code, language)
        
        output = result.stdout
        
        print(output)
        expected_output = TestCase.objects.filter(problem=problem_id).values_list('expected_output', flat=True)
        print(expected_output)
  
        # to be continued
        
        if result.get("error"):
            return Response({"error": result["error"]}, status=result["status"])

        return Response({
            "message": result["message"],
            "execution_result": result.get("result")
        }, status=result["status"])


import threading
from django.core.cache import cache  # Use Django's cache framework for simplicity

@method_decorator(csrf_exempt, name='dispatch')
class Judge0CallbackView(APIView):
    def put(self, request):
        try:
            print("Callback received")
            data = json.loads(request.body)
            
            # Extract problem ID or unique key (adjust as necessary)
            problem_id = data.get('problem_id')
            if not problem_id:
                return Response({"error": "Missing problem_id in callback"}, status=status.HTTP_400_BAD_REQUEST)
            
            # Save result in the cache or shared storage
            cache.set(f"judge0_result_{problem_id}", data, timeout=300)  # Store for 5 minutes
            
            # Notify any waiting threads (if applicable)
            cache_key = f"judge0_event_{problem_id}"
            event = cache.get(cache_key)
            if event:
                event.set()

            return Response({"message": "Callback processed successfully"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
