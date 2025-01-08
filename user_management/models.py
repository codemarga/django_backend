from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from coderun.models import Problem 


from django.db import models
from django.contrib.auth.models import User
from coderun.models import Problem  
from contest_management.models import Contest  


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.user.username


class UserProblem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='solved_problems')
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, related_name='solvers')
    points_awarded = models.IntegerField() 
    submission_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} solved {self.problem.title}"



@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
