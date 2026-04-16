from django.urls import path
from . import views

app_name = "questions"

urlpatterns = [
    path("", views.index, name="index"),
    path("hot/", views.hot, name="hot"),
    path("tag/<str:tag>/", views.tag_questions, name="tag"),
    path("question/<int:question_id>/", views.question_detail, name="question"),
    path("ask/", views.ask_question, name="ask"),
]
