from django.db.models import Count
from django.contrib.auth.models import User

from questions.models import Tag


def sidebar_data(request):
    popular_tags = Tag.objects.annotate(num_questions=Count("questions")).order_by(
        "-num_questions"
    )[:10]
    best_members = User.objects.annotate(num_answers=Count("answers")).order_by(
        "-num_answers"
    )[:5]

    return {
        "popular_tags": popular_tags,
        "best_members": best_members,
    }
