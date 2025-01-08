from django.urls import path
from .views import ProblemListView, ProblemDetailView, RunCodeView , Judge0CallbackView, TestCaseView

urlpatterns = [
    path('problems/', ProblemListView.as_view(), name='problem-list'),
    path('pbs/<int:pk>/', ProblemDetailView.as_view(), name='problem-detail'),
    path('runcode/', RunCodeView.as_view(), name='run-code'),
    path('judge0/callback/', Judge0CallbackView.as_view(), name='judge0_callback'),
    path('testcases/<int:pk>/', TestCaseView.as_view(), name='test-case'),
]