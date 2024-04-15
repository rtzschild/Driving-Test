"""
Author:
Susan Wagle
"""

# import the package
from django.contrib import admin

# Register your models here.
from .models import *

# Register Category
admin.site.register(Category)


class AnswerAdmin(admin.StackedInline):
    model = Answer


class QuestionAdmin(admin.ModelAdmin):
    inlines = [AnswerAdmin]


# Register Question
admin.site.register(Question, QuestionAdmin)
# Register Answer
admin.site.register(Answer)
# Register quiz result
admin.site.register(QuizResult)
