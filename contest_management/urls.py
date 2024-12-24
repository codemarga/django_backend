from django.urls import path
from .views import JoinContestView, SubmitContestCodeView, ContestScoresView,ContestListView,ContestProblemListView

urlpatterns = [
    path('contestList/', ContestListView.as_view(), name='contest_list'),
    path('contestproblems/', ContestProblemListView.as_view(), name='contest_problems'),
    path('join/', JoinContestView.as_view(), name='join_contest'),
    path('submit/', SubmitContestCodeView.as_view(), name='submit_contest_code'),
    path('scores/<int:contest_id>/', ContestScoresView.as_view(), name='contest_scores'),
]
