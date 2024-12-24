from django.urls import path
from .views import JoinContestView, SubmitContestCodeView, ContestScoresView

urlpatterns = [
    path('join/', JoinContestView.as_view(), name='join_contest'),
    path('submit/', SubmitContestCodeView.as_view(), name='submit_contest_code'),
    path('scores/<int:contest_id>/', ContestScoresView.as_view(), name='contest_scores'),
]
