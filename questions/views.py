from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse

from questions.mixins import AnswersPaginationMixin
from .utils import paginate
from .models import Question, Tag
from .forms import AskForm, AnswerForm


class IndexView(TemplateView):
    template_name = "questions/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        questions = Question.objects.new()
        page, paginator = paginate(questions, self.request, per_page=10)

        context.update(
            {"questions": page.object_list, "page": page, "paginator": paginator}
        )
        return context


class HotView(TemplateView):
    template_name = "questions/hot.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        questions = Question.objects.hot()
        page, paginator = paginate(questions, self.request, per_page=10)

        context.update(
            {"questions": page.object_list, "page": page, "paginator": paginator}
        )
        return context


class TagView(TemplateView):
    template_name = "questions/tag.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        tag_name = self.kwargs.get("tag")
        tag_obj = Tag.objects.by_name(tag_name)
        questions = Question.objects.by_tag(tag_name)
        page, paginator = paginate(questions, self.request, per_page=10)

        context.update(
            {
                "questions": page.object_list,
                "page": page,
                "paginator": paginator,
                "tag": tag_obj,
            }
        )
        return context


class QuestionDetailView(AnswersPaginationMixin, View):
    template_name = "questions/question.html"

    def get(self, request, *args, **kwargs):
        question = Question.objects.by_id(kwargs["question_id"])
        page, paginator = self.get_answers_page(question)
        form = AnswerForm()

        return render(
            request,
            self.template_name,
            self.build_question_context(question, page, paginator, form),
        )

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
        return render(
            request,
            self.template_name,
            self.build_question_context(question, page, paginator, form),
        )


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
