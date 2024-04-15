"""
Author:
Susan Wagle
"""
from django.apps import AppConfig


class QuizConfig(AppConfig):
    # This line specifies the default auto-generated field to use for models in the app.
    # In this case, it's set to use a BigAutoField, which is suitable for databases that support it.
    default_auto_field = 'django.db.models.BigAutoField'

    # This is the name of the app.
    name = 'Quiz'
