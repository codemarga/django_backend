from django.db import models
from django.contrib.auth.models import User
from coderun.models import Problem
from django.utils import timezone


class Contest(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    problems = models.ManyToManyField(Problem, related_name='contests')

    def __str__(self):
        return self.name


class ContestParticipation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='contest_participations')
    contest = models.ForeignKey(Contest, on_delete=models.CASCADE, related_name='participants')
    start_time = models.DateTimeField(auto_now_add=True)
    stoppage_time = models.DateTimeField()
    score = models.IntegerField(default=0)  # Score specific to this contest
    completed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.contest.name}"



class ContestSubmission(models.Model):
    participation = models.ForeignKey(ContestParticipation, on_delete=models.CASCADE, related_name='submissions')
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    submission_time = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[('SUCCESS', 'Success'), ('FAIL', 'Fail')])
    score_awarded = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.participation.user.username} - {self.problem.title}"
