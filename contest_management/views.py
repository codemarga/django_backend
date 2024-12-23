from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import ContestParticipation, ContestSubmission
from user_management.models import UserProfile
from coderun.RunCode import execute_code_with_callback
from coderun.complexity_checker import analyze_time_complexity
from django.http import JsonResponse
from django.views import View


class JoinContestView(View):
    def get(self, request):
        return JsonResponse({"message": "Join contest endpoint"})

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
