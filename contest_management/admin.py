from django.contrib import admin
from .models import Contest, ContestParticipation, ContestSubmission

@admin.register(ContestParticipation)
class ContestParticipationAdmin(admin.ModelAdmin):
    list_display = ('user', 'contest', 'score', 'stoppage_time', 'completed')
    search_fields = ('user__username', 'contest__name')
    list_filter = ('completed',)
