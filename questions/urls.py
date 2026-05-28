from django.urls import path
from . import views

app_name = "questions"

urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("hot/", views.HotView.as_view(), name="hot"),
    path("tag/<str:tag>/", views.TagView.as_view(), name="tag"),
    path(
        "question/<int:question_id>/",
        views.QuestionDetailView.as_view(),
        name="question",
    ),
    path("ask/", views.AskQuestionView.as_view(), name="ask"),

    path("ajax/vote/question/", views.vote_question, name="vote_question"),
    path("ajax/vote/answer/", views.vote_answer, name="vote_answer"),
    path("ajax/answer/correct/", views.mark_correct, name="mark_correct"),
]
