from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import models
from django.contrib.auth.hashers import make_password
from django.db.models import Subquery, Sum, OuterRef
from django.db.models.functions import Coalesce
from core.models import Profile
from questions.models import Tag, Question, Answer, QuestionLike, AnswerLike
from faker import Faker
import random

BATCH_SIZE = 5000
POOL_SIZE = 100


class Command(BaseCommand):
    help = "Fills database with mock data"

    def add_arguments(self, parser):
        parser.add_argument("ratio", type=int, help="Ratio for data generation")
        parser.add_argument(
            "--seed", type=int, default=42, help="Random seed for reproducibility"
        )

    def handle(self, *args, **kwargs):
        ratio, seed = kwargs["ratio"], kwargs["seed"]

        random.seed(seed)
        fake = Faker(seed=seed)

        self.stdout.write(
            self.style.SUCCESS(
                f'[SEED: {seed}] Starting to fill DB with ratio "{ratio}"...'
            )
        )

        # Using predefined pools will be better for mem and performance at all
        self.stdout.write("Generating text pools...")
        titles_pool = tuple(
            fake.sentence(nb_words=6).replace(".", "") for _ in range(POOL_SIZE)
        )
        texts_pool = tuple(fake.text(max_nb_chars=200) for _ in range(POOL_SIZE))
        answer_texts_pool = tuple(fake.text(max_nb_chars=100) for _ in range(POOL_SIZE))

        # Django Users
        self.stdout.write("Creating Django users...")
        fake_password = make_password("secretPasswords")

        users = User.objects.bulk_create(
            (
                User(
                    username=f"{fake.user_name()}_{i}",
                    email=f"{i}_{fake.email()}",
                    password=fake_password,
                )
                for i in range(ratio)
            ),
            batch_size=BATCH_SIZE,
        )
        user_ids = tuple(u.id for u in users)

        # Profiles
        self.stdout.write("Creating profiles...")
        Profile.objects.bulk_create(
            (Profile(user_id=uid) for uid in user_ids),
            batch_size=BATCH_SIZE,
        )

        # Tags
        self.stdout.write("Creating tags...")
        tags = Tag.objects.bulk_create(
            (Tag(name=f"{fake.word().lower()}_{i}") for i in range(ratio)),
            batch_size=BATCH_SIZE,
        )
        tag_ids = tuple(t.id for t in tags)

        # Questions
        self.stdout.write("Creating questions...")
        questions = Question.objects.bulk_create(
            (
                Question(
                    title=random.choice(titles_pool),
                    text=random.choice(texts_pool),
                    author_id=random.choice(user_ids),
                    rating=0,
                )
                for _ in range(ratio * 10)
            ),
            batch_size=BATCH_SIZE,
        )
        question_ids = tuple(q.id for q in questions)

        # Add tags to questions (3 for each) - only for newly created questions
        self.stdout.write("Adding tags to questions...")
        QuestionTags = Question.tags.through
        QuestionTags.objects.bulk_create(
            (
                QuestionTags(question_id=q_id, tag_id=t_id)
                for q_id in question_ids
                for t_id in random.sample(tag_ids, min(3, len(tag_ids)))
            ),
            batch_size=BATCH_SIZE,
            ignore_conflicts=True,
        )

        # Answers
        self.stdout.write("Creating answers...")
        answers = Answer.objects.bulk_create(
            (
                Answer(
                    # Only 1 correct among 10
                    text=random.choice(answer_texts_pool),
                    question_id=question_ids[i // 10],
                    author_id=random.choice(user_ids),
                    is_correct=(i % 10 == 0),
                    rating=0,
                )
                for i in range(ratio * 100)
            ),
            batch_size=BATCH_SIZE,
        )
        answer_ids = tuple(a.id for a in answers)

        # Likes
        self.stdout.write("Creating likes...")
        QuestionLike.objects.bulk_create(
            (
                QuestionLike(
                    user_id=random.choice(user_ids),
                    question_id=random.choice(question_ids),
                    value=random.choice([1, -1]),
                )
                for _ in range(ratio * 200)
            ),
            batch_size=BATCH_SIZE,
            ignore_conflicts=True,
        )
        AnswerLike.objects.bulk_create(
            (
                AnswerLike(
                    user_id=random.choice(user_ids),
                    answer_id=random.choice(answer_ids),
                    value=random.choice([1, -1]),
                )
                for _ in range(ratio * 200)
            ),
            batch_size=BATCH_SIZE,
            ignore_conflicts=True,
        )

        # Update ratings separately in 1 query for performance - only for new entities
        self.stdout.write("Updating ratings...")

        q_likes = (
            QuestionLike.objects.filter(question_id=OuterRef("pk"))
            .values("question_id")
            .annotate(total=Sum("value"))
            .values("total")
        )
        Question.objects.filter(id__in=question_ids).update(
            rating=Coalesce(Subquery(q_likes), 0)
        )

        a_likes = (
            AnswerLike.objects.filter(answer_id=OuterRef("pk"))
            .values("answer_id")
            .annotate(total=Sum("value"))
            .values("total")
        )
        Answer.objects.filter(id__in=answer_ids).update(
            rating=Coalesce(Subquery(a_likes), 0)
        )

        self.stdout.write(self.style.SUCCESS("Successfully filled DB!"))
