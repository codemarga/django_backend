from django.db import models
from django.contrib.auth.models import User
from coderun.models import Problem
from django.utils import timezone

from django.db import models
from django.contrib.auth.models import User
from coderun.models import Problem


class Contest(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    problems = models.ManyToManyField(
        Problem,
        related_name='contests',
        through='ContestProblem'
    )

    def __str__(self):
        return self.name


class ContestProblem(models.Model):
    contest = models.ForeignKey(Contest, on_delete=models.CASCADE, related_name='contest_problems')
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, related_name='contest_problems')
    points = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.contest.name} - {self.problem.title} - {self.points} points"


class ContestParticipation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='contest_participations')
    contest = models.ForeignKey(Contest, on_delete=models.CASCADE, related_name='participants')
    start_time = models.DateTimeField(auto_now_add=True)
    stoppage_time = models.DateTimeField(default = timezone.now() + timezone.timedelta(days=1))
    score = models.IntegerField(default=0) 
    completed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.contest.name}"



class ContestSubmission(models.Model):
    contest = models.ForeignKey(Contest, on_delete=models.CASCADE, related_name='submissions')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='contest_submissions')
    submission_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.contest.name} - {self.submission_time}"
