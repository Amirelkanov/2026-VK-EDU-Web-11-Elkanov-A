from django.shortcuts import get_object_or_404, render, redirect
from django.db.models import Count
from django.views.generic import TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from .utils import paginate
from .models import Question, Tag
from .forms import AskForm, AnswerForm


class IndexView(TemplateView):
    template_name = "questions/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        questions = (
            Question.objects.new()
            .select_related("author")
            .prefetch_related("tags")
            .annotate(answers_count=Count("answers"))
        )
        page, paginator = paginate(questions, self.request, per_page=10)

        context.update(
            {"questions": page.object_list, "page": page, "paginator": paginator}
        )
        return context


class HotView(TemplateView):
    template_name = "questions/hot.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        questions = (
            Question.objects.hot()
            .select_related("author")
            .prefetch_related("tags")
            .annotate(answers_count=Count("answers"))
        )
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
        tag_obj = get_object_or_404(Tag, name=tag_name)
        questions = (
            Question.objects.by_tag(tag_name)
            .select_related("author")
            .prefetch_related("tags")
            .annotate(answers_count=Count("answers"))
        )
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


class QuestionDetailView(View):
    template_name = "questions/question.html"

    def get(self, request, *args, **kwargs):
        question_id = self.kwargs.get("question_id")
        question = get_object_or_404(
            Question.objects.select_related("author")
            .prefetch_related("tags")
            .annotate(answers_count=Count("answers")),
            pk=question_id,
        )
        answers = question.answers.select_related("author").order_by(
            "created_at", "-rating"
        )
        page, paginator = paginate(answers, self.request, per_page=3)

        form = AnswerForm()

        context = {
            "question": question,
            "answers": page.object_list,
            "answers_count": question.answers_count,
            "page": page,
            "paginator": paginator,
            "form": form,
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(f"{reverse('core:login')}?next={request.path}")

        question_id = self.kwargs.get("question_id")
        question = get_object_or_404(Question, pk=question_id)

        form = AnswerForm(request.POST)
        if form.is_valid():
            answer = form.save(author=request.user, question=question)
            # Redirect to the last page of answers where the new answer is
            answers_count = question.answers.count()
            per_page = 3
            last_page = (answers_count - 1) // per_page + 1
            url = reverse("questions:question", kwargs={"question_id": question.id})
            return redirect(f"{url}?page={last_page}#answer-{answer.id}")

        # If form is invalid, re-render the page with errors
        question = get_object_or_404(
            Question.objects.select_related("author")
            .prefetch_related("tags")
            .annotate(answers_count=Count("answers")),
            pk=question_id,
        )
        answers = question.answers.select_related("author").order_by(
            "created_at", "-rating"
        )
        page, paginator = paginate(answers, self.request, per_page=3)

        context = {
            "question": question,
            "answers": page.object_list,
            "answers_count": question.answers_count,
            "page": page,
            "paginator": paginator,
            "form": form,
        }
        return render(request, self.template_name, context)


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
