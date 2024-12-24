from django.contrib import admin
from .models import Contest, ContestParticipation, ContestSubmission,ContestProblem


# Inline for ContestProblem to manage problem assignments directly from Contest admin page
class ContestProblemInline(admin.TabularInline):
    model = ContestProblem
    extra = 1  # Number of empty forms to display by default


@admin.register(Contest)
class ContestAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_time', 'end_time')
    search_fields = ('name',)
    list_filter = ('start_time', 'end_time')
    inlines = [ContestProblemInline]


@admin.register(ContestProblem)
class ContestProblemAdmin(admin.ModelAdmin):
    list_display = ('contest', 'problem', 'points')
    list_filter = ('contest', 'problem')
    search_fields = ('contest__name', 'problem__title')

@admin.register(ContestParticipation)
class ContestParticipationAdmin(admin.ModelAdmin):
    list_display = ('user', 'contest', 'score', 'stoppage_time', 'completed')
    search_fields = ('user__username', 'contest__name')
    list_filter = ('completed',)
