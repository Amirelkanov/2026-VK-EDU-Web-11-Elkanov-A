from django.db import models
from django.db.models import Count
from django.shortcuts import get_object_or_404

LIKE_CHOICES = (
    (1, "Like"),
    (-1, "Dislike"),
)


class TagManager(models.Manager):
    def by_name(self, name):
        return get_object_or_404(self, name=name)


class Tag(models.Model):
    name = models.SlugField(max_length=50, unique=True, verbose_name="Название")

    objects = TagManager()

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"

    def __str__(self):
        return self.name


class QuestionManager(models.Manager):
    def _with_relations(self):
        return self.select_related("author").prefetch_related("tags")

    def hot(self):
        return (
            self._with_relations()
            .annotate(answers_count=Count("answers"))
            .order_by("-rating", "-created_at")
        )

    def new(self):
        return (
            self._with_relations()
            .annotate(answers_count=Count("answers"))
            .order_by("-created_at")
        )

    def by_tag(self, tag_name):
        return (
            self._with_relations()
            .annotate(answers_count=Count("answers"))
            .filter(tags__name=tag_name)
            .order_by("-created_at")
        )

    def by_id(self, question_id):
        return get_object_or_404(
            self._with_relations().annotate(answers_count=Count("answers")),
            pk=question_id,
        )


class Question(models.Model):
    title = models.CharField(max_length=255, verbose_name="Заголовок")
    text = models.TextField(max_length=10000, verbose_name="Текст")
    author = models.ForeignKey(
        "auth.User",
        on_delete=models.CASCADE,
        related_name="questions",
        verbose_name="Автор",
    )
    tags = models.ManyToManyField("Tag", related_name="questions", verbose_name="Теги")
    rating = models.IntegerField(default=0, verbose_name="Рейтинг")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    objects = QuestionManager()

    class Meta:
        verbose_name = "Вопрос"
        verbose_name_plural = "Вопросы"

    def __str__(self):
        return self.title


class Answer(models.Model):
    text = models.TextField(max_length=10000, verbose_name="Текст")
    question = models.ForeignKey(
        "Question",
        on_delete=models.CASCADE,
        related_name="answers",
        verbose_name="Вопрос",
    )
    author = models.ForeignKey(
        "auth.User",
        on_delete=models.CASCADE,
        related_name="answers",
        verbose_name="Автор",
    )
    is_correct = models.BooleanField(default=False, verbose_name="Правильный ответ")
    rating = models.IntegerField(default=0, verbose_name="Рейтинг")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Ответ"
        verbose_name_plural = "Ответы"

    def __str__(self):
        return f'Ответ от {self.author.username} на "{self.question.title}"'


class QuestionLike(models.Model):
    user = models.ForeignKey(
        "auth.User",
        on_delete=models.CASCADE,
        related_name="question_likes",
        verbose_name="Пользователь",
    )
    question = models.ForeignKey(
        "Question",
        on_delete=models.CASCADE,
        related_name="likes",
        verbose_name="Вопрос",
    )
    value = models.SmallIntegerField(choices=LIKE_CHOICES, verbose_name="Значение")

    class Meta:
        verbose_name = "Лайк вопроса"
        verbose_name_plural = "Лайки вопросов"
        unique_together = ("user", "question")

    def __str__(self):
        return f"{self.user.username} -> {self.question.title} ({self.value})"


class AnswerLike(models.Model):
    user = models.ForeignKey(
        "auth.User",
        on_delete=models.CASCADE,
        related_name="answer_likes",
        verbose_name="Пользователь",
    )
    answer = models.ForeignKey(
        "Answer", on_delete=models.CASCADE, related_name="likes", verbose_name="Ответ"
    )
    value = models.SmallIntegerField(choices=LIKE_CHOICES, verbose_name="Значение")

    class Meta:
        verbose_name = "Лайк ответа"
        verbose_name_plural = "Лайки ответов"
        unique_together = ("user", "answer")

    def __str__(self):
        return f"{self.user.username} -> Ответ {self.answer.pk} ({self.value})"
