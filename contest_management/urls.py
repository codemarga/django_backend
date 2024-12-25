from django.urls import path
from .views import JoinContestView, SubmitContestProblemView, ContestScoresView,ContestListView,ContestProblemListView,ContestSubmissionView

urlpatterns = [
    path('contestList/', ContestListView.as_view(), name='contest_list'),
    path('contestproblems/', ContestProblemListView.as_view(), name='contest_problems'),
    path('join/', JoinContestView.as_view(), name='join_contest'),
    path('submit/', SubmitContestProblemView.as_view(), name='submit_contest_code'),
    path("contestsubmission/", ContestSubmissionView.as_view(), name="contest_submission"),
    path('scores/<int:contest_id>/', ContestScoresView.as_view(), name='contest_scores'),
]
