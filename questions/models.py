from django.db import models
from django.db.models import Count
from django.shortcuts import get_object_or_404

from questions.utils import LIKE_CHOICES
from django.db import transaction


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
    def get_user_votes(self, questions, user):
        if not user.is_authenticated or not questions:
            return {}
        question_ids = [q.id for q in questions]
        likes = QuestionLike.objects.filter(
            user=user, question_id__in=question_ids
        ).values_list("question_id", "value")
        return dict(likes)

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


class AnswerManager(models.Manager):
    def get_user_votes(self, answers, user):
        if not user.is_authenticated or not answers:
            return {}
        answer_ids = [a.id for a in answers]
        likes = AnswerLike.objects.filter(
            user=user, answer_id__in=answer_ids
        ).values_list("answer_id", "value")
        return dict(likes)

    def mark_correct(self, answer, is_correct):
        self.filter(pk=answer.pk).update(is_correct=bool(is_correct))


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

    objects = AnswerManager()

    class Meta:
        verbose_name = "Ответ"
        verbose_name_plural = "Ответы"

    def __str__(self):
        return f'Ответ от {self.author.username} на "{self.question.title}"'


class QuestionLikeManager(models.Manager):
    def toggle_like(self, user, question, value):
        with transaction.atomic():
            question = Question.objects.select_for_update().get(pk=question.pk)
            like, created = self.select_for_update().get_or_create(
                user=user, question=question, defaults={"value": value}
            )

            rating_delta = 0
            if not created:
                if like.value == value:
                    like.delete()
                    user_vote = 0
                    rating_delta = -value
                else:
                    rating_delta = value - like.value
                    like.value = value
                    like.save(update_fields=["value"])
                    user_vote = value
            else:
                user_vote = value
                rating_delta = value

            if rating_delta != 0:
                question.rating += rating_delta
                question.save(update_fields=["rating"])

            return question.rating, user_vote


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

    objects = QuestionLikeManager()

    class Meta:
        verbose_name = "Лайк вопроса"
        verbose_name_plural = "Лайки вопросов"
        unique_together = ("user", "question")

    def __str__(self):
        return f"{self.user.username} -> {self.question.title} ({self.value})"


class AnswerLikeManager(models.Manager):
    def toggle_like(self, user, answer, value):
        with transaction.atomic():
            answer = Answer.objects.select_for_update().get(pk=answer.pk)
            like, created = self.select_for_update().get_or_create(
                user=user, answer=answer, defaults={"value": value}
            )

            rating_delta = 0
            if not created:
                if like.value == value:
                    like.delete()
                    user_vote = 0
                    rating_delta = -value
                else:
                    rating_delta = value - like.value
                    like.value = value
                    like.save(update_fields=["value"])
                    user_vote = value
            else:
                user_vote = value
                rating_delta = value

            if rating_delta != 0:
                answer.rating += rating_delta
                answer.save(update_fields=["rating"])

            return answer.rating, user_vote


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

    objects = AnswerLikeManager()

    class Meta:
        verbose_name = "Лайк ответа"
        verbose_name_plural = "Лайки ответов"
        unique_together = ("user", "answer")

    def __str__(self):
        return f"{self.user.username} -> Ответ {self.answer.pk} ({self.value})"
