from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from .models import Problem , TestCase
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import json
from django.core.cache import cache 
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .utils import run_code
import base64
from user_management.models import User
from user_management.models import UserProblem



class ProblemListView(APIView):
    def get(self, request):
        problems = Problem.objects.all()
        problem_list = [
            {
                "id": problem.id,
                "title": problem.title,
                "description": problem.description,
                "difficulty": "Easy",
            }
            for problem in problems
        ]
        return JsonResponse(problem_list, safe=False, status=200)


class TestCaseView(APIView):
    def get(self, request,pk):
        try:
            test_cases = TestCase.objects.filter(problem=pk)
            test_case_list = [
                {
                    "id": test_case.id,
                    "input": test_case.input_data,
                    "output": test_case.expected_output,
                }
                for test_case in test_cases
            ]
            return JsonResponse(test_case_list, safe=False, status=200)
        except ObjectDoesNotExist:
            return JsonResponse({"error": "Problem not found"}, status=404)

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
                "category": [category.name for category in problem.categories.all()],
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


class RunCodeView(APIView):
    def post(self, request):
        problem_id = request.data.get("problem_id")
        code = request.data.get("code")
        language = request.data.get("language")
        
        print(problem_id, code, language)

        if not problem_id or not code or not language:
            return Response({"error": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST)

        result = run_code(problem_id, code, language)
        print(result)
        stdout = result['result'].get('stdout')
        
        if stdout:
            stdout = base64.b64decode(stdout).decode("utf-8")
            
        compile_output=result['result']['compile_output']
        if compile_output:
            compile_output = base64.b64decode(compile_output).decode("utf-8")
        
        description = result['result']['status']['description']
        stderr = result['result']['stderr']
        if stderr:
            stderr = base64.b64decode(stderr).decode("utf-8")
        time = result['result']['time']
        memory = result['result']['memory']
        state=result['status']
        
        problem = Problem.objects.get(id=problem_id)
        test_cases = TestCase.objects.filter(problem=problem_id)
        
        if description == "Accepted":
            expected_outputs = [test_case.expected_output for test_case in test_cases]
            print(expected_outputs)
            outputs = [eval(line) for line in stdout.strip().split('\n')]
            print(outputs)

            # Count matches
            match_count = sum(1 for i in range(len(expected_outputs)) if expected_outputs[i] == outputs[i])

            # Calculate score
            total_cases = len(expected_outputs)
            score = 0
            if match_count > 0:
                score = (2 ** -(total_cases - match_count)) * problem.difficulty_wise_points

            print(f"Matched Cases: {match_count}/{total_cases}")
            print(f"Score: {score}")

            email = request.data.get("email")
            user = User.objects.get(email=email)
            time_taken_penalty = int(request.data.get("time")) / 60000
            compile_time_penalty = float(result['result']['time']) * 1000
            print(email, user, problem, time_taken_penalty, compile_time_penalty, score)
            score = score - time_taken_penalty - compile_time_penalty
            user_problem, created = UserProblem.objects.update_or_create(
                user=user, problem=problem,
                defaults={'points_awarded': score}
            )
        
        
        expected_output = TestCase.objects.filter(problem=problem_id).values_list('expected_output', flat=True)
        print(expected_output)
  
        # to be continued
        
        return Response({
            "stdout": stdout,
            "compile_output": compile_output,
            "description": description,
            "stderr": stderr,
            "time": time,
            "memory": memory,
            "state": state,
        }, status=result["status"])

@method_decorator(csrf_exempt, name='dispatch')
class Judge0CallbackView(APIView):
    def put(self, request):
        try:
            print("Callback received")
            data = json.loads(request.body)
            
            # Save result in the cache or shared storage
            cache.set(f"judge0_result", data, timeout=300)  # Store result for 5 minutes
            
            # Set a flag to notify waiting threads
            cache.set(f"judge0_flag", True, timeout=300)

            return Response({"message": "Callback processed successfully"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
