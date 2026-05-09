from django.shortcuts import get_object_or_404
from django.db.models import Count
from django.views.generic import TemplateView
from .utils import paginate
from .models import Question, Tag


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


class QuestionDetailView(TemplateView):
    template_name = "questions/question.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        question_id = self.kwargs.get("question_id")
        question = get_object_or_404(
            Question.objects.select_related("author")
            .prefetch_related("tags")
            .annotate(answers_count=Count("answers")),
            pk=question_id,
        )
        answers = question.answers.select_related("author").order_by(
            "-rating", "-created_at"
        )
        page, paginator = paginate(answers, self.request, per_page=3)

        context.update(
            {
                "question": question,
                "answers": page.object_list,
                "answers_count": question.answers_count,
                "page": page,
                "paginator": paginator,
            }
        )
        return context


class AskQuestionView(TemplateView):
    template_name = "questions/ask.html"
