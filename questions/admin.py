from django.contrib import admin
from .models import Tag, Question, Answer, QuestionLike, AnswerLike


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


class AnswerInline(admin.StackedInline):
    model = Answer
    extra = 1
    raw_id_fields = ("author",)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "rating", "created_at")
    search_fields = ("title", "text")
    list_filter = ("created_at",)
    raw_id_fields = ("author",)
    filter_horizontal = ("tags",)
    inlines = [AnswerInline]

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("author")
            .prefetch_related("tags")
        )


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ("question", "author", "is_correct", "rating", "created_at")
    search_fields = ("text",)
    list_filter = ("is_correct", "created_at")
    raw_id_fields = ("question", "author")

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("question", "author")


@admin.register(QuestionLike)
class QuestionLikeAdmin(admin.ModelAdmin):
    list_display = ("user", "question", "value")
    raw_id_fields = ("user", "question")

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("user", "question")


@admin.register(AnswerLike)
class AnswerLikeAdmin(admin.ModelAdmin):
    list_display = ("user", "answer", "value")
    raw_id_fields = ("user", "answer")

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("user", "answer")
