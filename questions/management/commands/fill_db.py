from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.db.models import Subquery, Sum, OuterRef
from django.db.models.functions import Coalesce
import pgtrigger
from core.models import Profile
from questions.models import Tag, Question, Answer, QuestionLike, AnswerLike
from faker import Faker
import random

BATCH_SIZE = 5000
POOL_SIZE = 100


class Command(BaseCommand):
    help = "Fills empty database with mock data"

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

        users_gen = (
            User(
                username=f"{fake.user_name()}_{i}",
                email=f"{i}_{fake.email()}",
                password=fake_password,
            )
            for i in range(ratio)
        )
        User.objects.bulk_create(users_gen, batch_size=BATCH_SIZE)

        user_ids = tuple(User.objects.values_list("id", flat=True))

        # Profiles
        self.stdout.write("Creating profiles from Django users...")
        profiles_gen = (Profile(user_id=uid) for uid in user_ids)
        Profile.objects.bulk_create(profiles_gen, batch_size=BATCH_SIZE)

        # Tags
        self.stdout.write("Creating tags...")
        tags_gen = (Tag(name=f"{fake.word()}_{i}") for i in range(ratio))
        Tag.objects.bulk_create(tags_gen, batch_size=BATCH_SIZE)
        tag_ids = tuple(Tag.objects.values_list("id", flat=True))

        # Questions
        self.stdout.write("Creating questions...")
        questions_gen = (
            Question(
                title=random.choice(titles_pool),
                text=random.choice(texts_pool),
                author_id=random.choice(user_ids),
                rating=0,
            )
            for i in range(ratio * 10)
        )
        Question.objects.bulk_create(questions_gen, batch_size=BATCH_SIZE)
        question_ids = tuple(Question.objects.values_list("id", flat=True))

        # Add tags to questions (3 for each)
        self.stdout.write("Adding tags to questions...")
        QuestionTags = Question.tags.through

        question_tags_gen = (
            QuestionTags(question_id=q_id, tag_id=t_id)
            for q_id in question_ids
            for t_id in random.sample(tag_ids, 3)
        )
        QuestionTags.objects.bulk_create(question_tags_gen, batch_size=BATCH_SIZE)

        # Answers
        self.stdout.write("Creating answers...")
        answers_gen = (
            # Only 1 correct among 10
            Answer(
                text=random.choice(answer_texts_pool),
                question_id=question_ids[i // 10],
                author_id=random.choice(user_ids),
                is_correct=(i % 10 == 0),
                rating=0,
            )
            for i in range(ratio * 100)
        )
        Answer.objects.bulk_create(answers_gen, batch_size=BATCH_SIZE)
        answer_ids = tuple(Answer.objects.values_list("id", flat=True))

        # Likes
        self.stdout.write("Creating likes...")

        question_likes_gen = (
            QuestionLike(
                user_id=random.choice(user_ids),
                question_id=random.choice(question_ids),
                value=random.choice([1, -1]),
            )
            for _ in range(ratio * 200)
        )
        answer_likes_gen = (
            AnswerLike(
                user_id=random.choice(user_ids),
                answer_id=random.choice(answer_ids),
                value=random.choice([1, -1]),
            )
            for _ in range(ratio * 200)
        )

        with pgtrigger.ignore():
            QuestionLike.objects.bulk_create(
                question_likes_gen, batch_size=BATCH_SIZE, ignore_conflicts=True
            )
            AnswerLike.objects.bulk_create(
                answer_likes_gen, batch_size=BATCH_SIZE, ignore_conflicts=True
            )

        # Update ratings separately in 1 query for performance
        self.stdout.write("Updating ratings...")

        likes_subquery = (
            QuestionLike.objects.filter(question_id=OuterRef("pk"))
            .values("question_id")
            .annotate(total=Sum("value"))
            .values("total")
        )
        Question.objects.update(rating=Coalesce(Subquery(likes_subquery), 0))

        answer_likes_subquery = (
            AnswerLike.objects.filter(answer_id=OuterRef("pk"))
            .values("answer_id")
            .annotate(total=Sum("value"))
            .values("total")
        )
        Answer.objects.update(rating=Coalesce(Subquery(answer_likes_subquery), 0))

        self.stdout.write(self.style.SUCCESS("Successfully filled DB!"))
