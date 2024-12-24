from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    total_score = models.IntegerField(default=0)  # Total points across all contests
    contests_participated = models.IntegerField(default=0)  # Number of contests participated
    last_submission_time = models.DateTimeField(blank=True, null=True)  # Track the last submission time
    current_contest_id = models.IntegerField(blank=True, null=True)  # Track ongoing contest (if any)

    def __str__(self):
        return self.user.username


# Automatically create UserProfile when a User is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
