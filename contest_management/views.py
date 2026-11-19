from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import ContestParticipation, ContestSubmission, Contest,ContestProblem
from user_management.models import UserProfile
from coderun.RunCode import execute_code_submission
from coderun.complexity_checker import analyze_time_complexity
from django.http import JsonResponse
from django.views import View
from django.contrib.auth.models import User
from coderun.utils import run_code
from django.utils.timezone import localtime



class ContestListView(APIView):
    def get(self, request):
        contests = Contest.objects.all()
        current_time = timezone.now()
        
        contest_data = []
        for contest in contests:
            time_until_start = contest.start_time - current_time
            contest_data.append({
                "id": contest.id,
                "name": contest.name,
                "description": contest.description,
                "start_time": contest.start_time,
                "end_time": contest.end_time,
                "time_until_start": str(time_until_start) if time_until_start.total_seconds() > 0 else "Contest has started"
            })

        return Response({"contests": contest_data}, status=status.HTTP_200_OK)
    
class ContestProblemListView(APIView):
    def get(self, request):
        contest_id = request.query_params.get('contest_id')
        print(contest_id)
        try:
            contest = Contest.objects.get(id=contest_id)
        except Contest.DoesNotExist:
            return Response({"error": "Contest not found"}, status=status.HTTP_404_NOT_FOUND)

        contest_problems = ContestProblem.objects.filter(contest=contest)
        problem_data = []
        time_duration =  contest.end_time - contest.start_time 
        days, seconds = time_duration.days, time_duration.seconds
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        formatted_duration = f"{days}d {hours}h {minutes}m {seconds}s"

        for contest_problem in contest_problems:
            problem = contest_problem.problem
            problem_data.append({
                "id": problem.id,
                "title": problem.title,
                "description": problem.description,
                "categories": [category.name for category in problem.categories.all()],
                "points": contest_problem.points
            })

        return Response({
            "contest_name": contest.name,
            "contest_id": contest_id,
            "contest_description": contest.description,
            "start_time": localtime(contest.start_time).strftime("%Y-%m-%d %H:%M:%S"),
            "time_duration": formatted_duration,
            "problems": problem_data
        }, status=status.HTTP_200_OK)
        
class JoinContestView(APIView):
    """Identifies the user and the contest in which they want to participate."""

    def post(self, request):
        email = request.data.get('email')
        contest_id = request.data.get('contest_id')
        print(f"Join contest: email={email}, contest_id={contest_id}")

        if not contest_id:
            return Response({"error": "Contest ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            contest = Contest.objects.get(id=contest_id)
        except Contest.DoesNotExist:
            return Response({"error": "Contest not found"}, status=status.HTTP_404_NOT_FOUND)

        user = None
        if email:
            user = User.objects.filter(email=email).first()
        if not user:
            user = User.objects.first()

        if user:
            participation, created = ContestParticipation.objects.get_or_create(user=user, contest=contest)
            if created:
                return Response({"message": "User joined contest successfully", "status": "success"}, status=status.HTTP_201_CREATED)
            else:
                return Response({"message": "User already joined contest", "status": "success"}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "Joined contest as guest", "status": "success"}, status=status.HTTP_200_OK)


class SubmitContestProblemView(APIView):
    def post(self, request):
        import base64
        from coderun.models import TestCase

        email = request.data.get('email')
        user_id = request.data.get('user_id')
        problem_id = request.data.get('problem_id')
        code = request.data.get('code')
        language = request.data.get('language', 'python')
        contest_id = request.data.get('contest_id')

        print(f"SubmitContestProblem: problem_id={problem_id}, contest_id={contest_id}, language={language}")

        if not problem_id or not code:
            return Response({"error": "Missing problem_id or code"}, status=status.HTTP_400_BAD_REQUEST)

        # Find user
        user = None
        if email:
            user = User.objects.filter(email=email).first()
        if not user and user_id:
            user = User.objects.filter(id=user_id).first()
        if not user:
            user = User.objects.first()

        contest = None
        if contest_id:
            contest = Contest.objects.filter(id=contest_id).first()

        participation = None
        if user and contest:
            participation, _ = ContestParticipation.objects.get_or_create(user=user, contest=contest)

        # Calculate time bonus
        time_bonus = 0
        if participation:
            current_time = timezone.now()
            start_time = participation.start_time or current_time
            stoppage_time = participation.stoppage_time or (start_time + timezone.timedelta(hours=2))
            time_duration = (stoppage_time - start_time).total_seconds()
            time_taken = (current_time - start_time).total_seconds()
            if time_duration > 0 and time_taken < time_duration:
                time_bonus = round(((time_duration - time_taken) / time_duration) * 100, 1)

        # Run the code
        run_code_result = run_code(problem_id, code, language)
        exec_res = run_code_result.get('result', {})

        stdout_b64 = exec_res.get('stdout')
        stderr_b64 = exec_res.get('stderr')
        compile_b64 = exec_res.get('compile_output')

        stdout = base64.b64decode(stdout_b64).decode('utf-8', errors='replace') if stdout_b64 else ""
        stderr = base64.b64decode(stderr_b64).decode('utf-8', errors='replace') if stderr_b64 else ""
        compile_output = base64.b64decode(compile_b64).decode('utf-8', errors='replace') if compile_b64 else ""
        description = exec_res.get('status', {}).get('description', 'Unknown')
        exec_time = exec_res.get('time', '0')

        # Test case evaluation
        test_cases = TestCase.objects.filter(problem=problem_id)
        expected_outputs = [tc.expected_output for tc in test_cases]
        matched_cases = 0
        total_cases = len(expected_outputs)

        if description == "Accepted" and stdout and total_cases > 0:
            try:
                actual_lines = [eval(line) for line in stdout.strip().split('\n') if line.strip()]
                matched_cases = sum(1 for i in range(min(total_cases, len(actual_lines))) if expected_outputs[i] == actual_lines[i])
            except Exception as e:
                print(f"Error evaluating test cases: {e}")

        test_case_bonus = round((matched_cases / total_cases) * 100) if total_cases > 0 else (100 if description == "Accepted" else 0)

        # Complexity bonus
        complexity_bonus = 0
        if language == 'python' and test_case_bonus >= 50:
            try:
                complexity_result = analyze_time_complexity(code)
                if isinstance(complexity_result, dict):
                    complexity_bonus = complexity_result.get('complexity_bonus', 0)
            except Exception:
                pass

        total_score = round(test_case_bonus + (time_bonus * 0.2) + complexity_bonus)

        # Save submission
        contest_score = 0
        if participation:
            participation.score += total_score
            participation.save()
            contest_score = participation.score

        if user and contest:
            try:
                ContestSubmission.objects.create(contest=contest, user=user)
            except Exception as e:
                print(f"Failed to log submission: {e}")

        return Response({
            "message": "Code submitted successfully",
            "description": description,
            "stdout": stdout,
            "stderr": stderr,
            "compile_output": compile_output,
            "time": exec_time,
            "matched_cases": matched_cases,
            "total_cases": total_cases,
            "test_case_bonus": test_case_bonus,
            "complexity_bonus": complexity_bonus,
            "time_bonus": time_bonus,
            "total_score": total_score,
            "contest_score": contest_score,
        }, status=status.HTTP_200_OK)

class ContestSubmissionView(APIView):
    def post(self, request):
        user = request.data.get('user_id')
        contest_id = request.data.get('contest_id')
        submission = ContestSubmission.objects.create(user=user, contest_id=contest_id)
        return Response({
            "message":"Contest Submission Successful"
        }, status=status.HTTP_200_OK)

class ContestScoresView(APIView):
    def get(self, request, contest_id):
        user = request.user

        try:
            participation = ContestParticipation.objects.get(user=user, contest_id=contest_id)
        except ContestParticipation.DoesNotExist:
            return Response({"error": "User did not participate in this contest"}, status=status.HTTP_404_NOT_FOUND)

        return Response({
            "contest_name": participation.contest.name,
            "contest_score": participation.score,
            "total_score": user.profile.total_score
        }, status=status.HTTP_200_OK)
