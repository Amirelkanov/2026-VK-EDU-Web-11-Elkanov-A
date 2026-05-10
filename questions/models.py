import pgtrigger
from django.db import models
from django.contrib.auth.models import User

LIKE_CHOICES = (
    (1, "Like"),
    (-1, "Dislike"),
)


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="Название")

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"

    def __str__(self):
        return self.name


class QuestionManager(models.Manager):
    def hot(self):
        return self.order_by("-rating", "-created_at")

    def new(self):
        return self.order_by("-created_at")

    def by_tag(self, tag_name):
        return self.filter(tags__name=tag_name).order_by("-created_at")


class Question(models.Model):
    title = models.CharField(max_length=255, verbose_name="Заголовок")
    text = models.TextField(verbose_name="Текст")
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="questions", verbose_name="Автор"
    )
    tags = models.ManyToManyField(Tag, related_name="questions", verbose_name="Теги")
    rating = models.IntegerField(default=0, verbose_name="Рейтинг")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    objects = QuestionManager()

    class Meta:
        verbose_name = "Вопрос"
        verbose_name_plural = "Вопросы"

    def __str__(self):
        return self.title


class Answer(models.Model):
    text = models.TextField(verbose_name="Текст")
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="answers",
        verbose_name="Вопрос",
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="answers", verbose_name="Автор"
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
        User,
        on_delete=models.CASCADE,
        related_name="question_likes",
        verbose_name="Пользователь",
    )
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name="likes", verbose_name="Вопрос"
    )
    value = models.SmallIntegerField(choices=LIKE_CHOICES, verbose_name="Значение")

    class Meta:
        verbose_name = "Лайк вопроса"
        verbose_name_plural = "Лайки вопросов"
        unique_together = ("user", "question")
        triggers = [
            pgtrigger.Trigger(
                name="update_rating_on_insert",
                operation=pgtrigger.Insert,
                when=pgtrigger.After,
                func=pgtrigger.Func(
                    "UPDATE questions_question "
                    "SET rating = rating + NEW.value "
                    "WHERE id = NEW.question_id; "
                    "RETURN NEW;"
                ),
            ),
            pgtrigger.Trigger(
                name="update_rating_on_update",
                operation=pgtrigger.Update,
                when=pgtrigger.After,
                func=pgtrigger.Func(
                    "UPDATE questions_question "
                    "SET rating = rating - OLD.value + NEW.value "
                    "WHERE id = NEW.question_id; "
                    "RETURN NEW;"
                ),
            ),
            pgtrigger.Trigger(
                name="update_rating_on_delete",
                operation=pgtrigger.Delete,
                when=pgtrigger.After,
                func=pgtrigger.Func(
                    "UPDATE questions_question "
                    "SET rating = rating - OLD.value "
                    "WHERE id = OLD.question_id; "
                    "RETURN OLD;"
                ),
            ),
        ]

    def __str__(self):
        return f"{self.user.username} -> {self.question.title} ({self.value})"


class AnswerLike(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="answer_likes",
        verbose_name="Пользователь",
    )
    answer = models.ForeignKey(
        Answer, on_delete=models.CASCADE, related_name="likes", verbose_name="Ответ"
    )
    value = models.SmallIntegerField(choices=LIKE_CHOICES, verbose_name="Значение")

    class Meta:
        verbose_name = "Лайк ответа"
        verbose_name_plural = "Лайки ответов"
        unique_together = ("user", "answer")
        triggers = [
            pgtrigger.Trigger(
                name="update_rating_on_insert",
                operation=pgtrigger.Insert,
                when=pgtrigger.After,
                func=pgtrigger.Func(
                    "UPDATE questions_answer "
                    "SET rating = rating + NEW.value "
                    "WHERE id = NEW.answer_id; "
                    "RETURN NEW;"
                ),
            ),
            pgtrigger.Trigger(
                name="update_rating_on_update",
                operation=pgtrigger.Update,
                when=pgtrigger.After,
                func=pgtrigger.Func(
                    "UPDATE questions_answer "
                    "SET rating = rating - OLD.value + NEW.value "
                    "WHERE id = NEW.answer_id; "
                    "RETURN NEW;"
                ),
            ),
            pgtrigger.Trigger(
                name="update_rating_on_delete",
                operation=pgtrigger.Delete,
                when=pgtrigger.After,
                func=pgtrigger.Func(
                    "UPDATE questions_answer "
                    "SET rating = rating - OLD.value "
                    "WHERE id = OLD.answer_id; "
                    "RETURN OLD;"
                ),
            ),
        ]

    def __str__(self):
        return f"{self.user.username} -> Ответ {self.answer.pk} ({self.value})"
