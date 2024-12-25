from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import ContestParticipation, ContestSubmission, Contest,ContestProblem
from user_management.models import UserProfile
from coderun.RunCode import execute_code_with_callback
from coderun.complexity_checker import analyze_time_complexity
from django.http import JsonResponse
from django.views import View
from django.contrib.auth.models import User



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
        contest_id = request.data.get('contest_id')
        print(contest_id)
        try:
            contest = Contest.objects.get(id=contest_id)
        except Contest.DoesNotExist:
            return Response({"error": "Contest not found"}, status=status.HTTP_404_NOT_FOUND)

        contest_problems = ContestProblem.objects.filter(contest=contest)
        problem_data = []

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
            "problems": problem_data
        }, status=status.HTTP_200_OK)
        

class JoinContestView(APIView):
    """Identifies the user and the contest in which they want to participate."""

    def post(self, request):
        user = request.data.get('user')  # Ensures authenticated user is used
        contest_id = request.data.get('contest_id')
        print(user)
        print(contest_id)
        
        user = User.objects.get(id=user)
        if not contest_id:
            return Response({"error": "Contest ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            contest = Contest.objects.get(id=contest_id)
        except Contest.DoesNotExist:
            return Response({"error": "Contest not found"}, status=status.HTTP_404_NOT_FOUND)

        participation, created = ContestParticipation.objects.get_or_create(user=user, contest=contest)
        
        if created:
            return Response({"message": "User joined contest successfully"}, status=status.HTTP_201_CREATED)
        else:
            return Response({"message": "User already joined contest"}, status=status.HTTP_200_OK)



class SubmitContestCodeView(APIView):
    def post(self, request):
        user = request.user
        problem_id = request.data.get('problem_id')
        code = request.data.get('code')
        language = request.data.get('language')

        try:
            participation = ContestParticipation.objects.get(user=user, completed=False)
        except ContestParticipation.DoesNotExist:
            return Response({"error": "No active contest participation found"}, status=status.HTTP_400_BAD_REQUEST)

        current_time = timezone.now()
        if current_time > participation.stoppage_time:
            time_bonus = 5
        else:
            time_bonus = 10

        # Execute code
        callback_url = "http://localhost:8000/judge0/callback/"
        execute_code_with_callback(language, code, '', '', [], problem_id, callback_url)

        # Assume code execution succeeded and test cases passed
        complexity_result = analyze_time_complexity(code)
        best_complexity = complexity_result.get('time_complexity') == "O(n)"  # Example best case
        complexity_bonus = 5 if best_complexity else 0

        total_score = time_bonus + complexity_bonus

        # Update Contest Participation (contest-specific score)
        participation.score += total_score
        participation.save()

        # Update User Profile (cumulative total score)
        user_profile = UserProfile.objects.get(user=user)
        user_profile.total_score += total_score
        user_profile.save()

        # Log submission
        ContestSubmission.objects.create(
            participation=participation,
            problem_id=problem_id,
            status="SUCCESS",
            score_awarded=total_score
        )

        return Response({
            "message": "Code submitted successfully",
            "contest_score": participation.score,
            "total_score": user_profile.total_score,
            "time_bonus": time_bonus,
            "complexity_bonus": complexity_bonus
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
