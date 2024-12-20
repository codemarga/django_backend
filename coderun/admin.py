from django.contrib import admin
from .models import Problem, Category, TestCase


@admin.register(Problem)
class ProblemAdmin(admin.ModelAdmin):
    list_display = ('title', 'class_name', 'method_name', 'list_categories')
    list_filter = ('categories',)
    search_fields = ('title', 'description', 'class_name', 'method_name')
    ordering = ('title',)
    fields = (
        'title',
        'description',
        'examples',
        'class_name',
        'method_name',
        'default_code',
        'driver_template',
        'constraints',
        'followup',
        'categories',
    )

    def list_categories(self, obj):
        return ", ".join([category.name for category in obj.categories.all()])
    list_categories.short_description = "Categories"


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(TestCase)
class TestCaseAdmin(admin.ModelAdmin):
    list_display = ('problem', 'input_data', 'expected_output')
    search_fields = ('problem__title', 'input_data', 'expected_output')
    ordering = ('problem',)
