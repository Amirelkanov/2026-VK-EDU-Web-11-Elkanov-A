from core.auth import get_user, is_authenticated
from data.core.mock_data import MOCK_USERS
from questions.utils import get_popular_tags


def user_context(request):
    return {
        "user": get_user(request),
    }


def best_members_context(request):
    return {
        "best_members": [user["nickname"] for user in MOCK_USERS],
    }


def popular_tags_context(request):
    return {
        "popular_tags": get_popular_tags(10),
    }
