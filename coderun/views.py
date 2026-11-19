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
        if not Problem.objects.exists():
            try:
                from scripts.populate_all_problems import seed_all_problems
                seed_all_problems()
            except Exception as e:
                print("Auto-seeding error:", e)

        problems = Problem.objects.all()
        difficulty_map = {500: "Easy", 1000: "Medium", 1500: "Hard"}
        problem_list = [
            {
                "id": problem.id,
                "title": problem.title,
                "description": problem.description,
                "difficulty": difficulty_map.get(problem.difficulty_wise_points, "Easy"),
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

        try:
            result = run_code(problem_id, code, language)
            print(result)
            
            # Handle error / timeout cases
            if "error" in result:
                return Response({"error": result["error"]}, status=result.get("status", status.HTTP_500_INTERNAL_SERVER_ERROR))
            
            if "result" not in result:
                return Response({"error": "Execution timed out or failed"}, status=status.HTTP_504_GATEWAY_TIMEOUT)
            
            exec_result = result['result']
            
            stdout = exec_result.get('stdout')
            if stdout:
                stdout = base64.b64decode(stdout).decode("utf-8")
                
            compile_output = exec_result.get('compile_output')
            if compile_output:
                compile_output = base64.b64decode(compile_output).decode("utf-8")
            
            description = exec_result.get('status', {}).get('description', 'Unknown')
            stderr = exec_result.get('stderr')
            if stderr:
                stderr = base64.b64decode(stderr).decode("utf-8")
            time_val = exec_result.get('time')
            memory = exec_result.get('memory')
            state = result.get('status')
            
            problem = Problem.objects.get(id=problem_id)
            test_cases = TestCase.objects.filter(problem=problem_id)
            
            if description == "Accepted" and stdout:
                try:
                    expected_outputs = [test_case.expected_output for test_case in test_cases]
                    print(expected_outputs)
                    outputs = [eval(line) for line in stdout.strip().split('\n') if line.strip()]
                    print(outputs)

                    # Count matches
                    match_count = sum(1 for i in range(min(len(expected_outputs), len(outputs))) if expected_outputs[i] == outputs[i])

                    # Calculate score
                    total_cases = len(expected_outputs)
                    score = 0
                    if match_count > 0:
                        score = (2 ** -(total_cases - match_count)) * problem.difficulty_wise_points

                    print(f"Matched Cases: {match_count}/{total_cases}")
                    print(f"Score: {score}")

                    email = request.data.get("email")
                    if email:
                        try:
                            user = User.objects.get(email=email)
                            time_taken_penalty = int(request.data.get("time", 0)) / 60000
                            compile_time_penalty = float(exec_result.get('time', 0)) * 1000
                            print(email, user, problem, time_taken_penalty, compile_time_penalty, score)
                            score = score - time_taken_penalty - compile_time_penalty
                            user_problem, created = UserProblem.objects.update_or_create(
                                user=user, problem=problem,
                                defaults={'points_awarded': score}
                            )
                        except User.DoesNotExist:
                            print(f"User with email {email} not found, skipping score update")
                except Exception as e:
                    print(f"Error during test case comparison: {e}")
            
            return Response({
                "stdout": stdout,
                "compile_output": compile_output,
                "description": description,
                "stderr": stderr,
                "time": time_val,
                "memory": memory,
                "state": state,
            }, status=result["status"])
        except Exception as e:
            print(f"RunCodeView error: {e}")
            import traceback
            traceback.print_exc()
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
