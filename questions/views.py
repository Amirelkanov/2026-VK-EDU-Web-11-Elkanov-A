from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required

from questions.mixins import AnswersMixin, QuestionListMixin
from .utils import json_error
from .models import Question, Tag, Answer, QuestionLike, AnswerLike
from .forms import AskForm, AnswerForm, VoteForm, MarkCorrectForm


class IndexView(QuestionListMixin, TemplateView):
    template_name = "questions/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        questions = Question.objects.new()
        context.update(self.get_questions_context(questions))
        return context


class HotView(QuestionListMixin, TemplateView):
    template_name = "questions/hot.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        questions = Question.objects.hot()
        context.update(self.get_questions_context(questions))
        return context


class TagView(QuestionListMixin, TemplateView):
    template_name = "questions/tag.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        tag_name = self.kwargs.get("tag")
        tag_obj = Tag.objects.by_name(tag_name)
        questions = Question.objects.by_tag(tag_name)

        context.update(self.get_questions_context(questions))
        context["tag"] = tag_obj
        return context


class QuestionDetailView(AnswersMixin, View):
    template_name = "questions/question.html"

    def get(self, request, *args, **kwargs):
        question = Question.objects.by_id(kwargs["question_id"])
        page, paginator = self.get_answers_page(question)
        form = AnswerForm()

        ctx = self.build_question_context(question, page, paginator, form)
        return render(request, self.template_name, ctx)

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(f"{reverse('core:login')}?next={request.path}")

        question = Question.objects.by_id(kwargs["question_id"])
        form = AnswerForm(request.POST)

        if form.is_valid():
            # We assume that new answer on last page
            answer = form.save(author=request.user, question=question)
            answers_count = question.answers.count()
            last_page = (answers_count - 1) // self.answers_per_page + 1
            url = reverse("questions:question", kwargs={"question_id": question.id})

            return redirect(f"{url}?page={last_page}#answer-{answer.id}")

        page, paginator = self.get_answers_page(question)
        ctx = self.build_question_context(question, page, paginator, form)
        return render(request, self.template_name, ctx)


class AskQuestionView(LoginRequiredMixin, View):
    template_name = "questions/ask.html"
    login_url = "core:login"

    def get(self, request, *args, **kwargs):
        form = AskForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request, *args, **kwargs):
        form = AskForm(request.POST)
        if form.is_valid():
            question = form.save(author=request.user)
            return redirect("questions:question", question_id=question.id)
        return render(request, self.template_name, {"form": form})


@require_POST
@login_required(login_url="core:login")
def vote_question(request):
    form = VoteForm(request.POST)
    if not form.is_valid():
        return json_error("Invalid parameters", status=400, details=form.errors)

    question_id = form.cleaned_data["target_id"]
    value = form.cleaned_data["value"]
    question = get_object_or_404(Question, pk=question_id)

    rating, user_vote = QuestionLike.objects.toggle_like(request.user, question, value)

    return JsonResponse({"ok": True, "rating": rating, "user_vote": user_vote})


@require_POST
@login_required(login_url="core:login")
def vote_answer(request):
    form = VoteForm(request.POST)
    if not form.is_valid():
        return json_error("Invalid parameters", status=400, details=form.errors)

    answer_id = form.cleaned_data["target_id"]
    value = form.cleaned_data["value"]
    answer = get_object_or_404(Answer, pk=answer_id)

    rating, user_vote = AnswerLike.objects.toggle_like(request.user, answer, value)

    return JsonResponse({"ok": True, "rating": rating, "user_vote": user_vote})


@require_POST
@login_required(login_url="core:login")
def mark_correct(request):
    form = MarkCorrectForm(request.POST)
    if not form.is_valid():
        return json_error("Invalid parameters", status=400, details=form.errors)

    question_id = form.cleaned_data["question_id"]
    answer_id = form.cleaned_data["answer_id"]
    is_correct = form.cleaned_data["is_correct"]

    question = get_object_or_404(Question, pk=question_id)
    if question.author_id != request.user.id:
        return json_error(
            "Only the question author can mark a correct answer", status=403
        )

    answer = get_object_or_404(Answer, pk=answer_id, question=question)

    Answer.objects.mark_correct(answer, is_correct)

    return JsonResponse(
        {"ok": True, "answer_id": answer.pk, "is_correct": bool(is_correct)}
    )
