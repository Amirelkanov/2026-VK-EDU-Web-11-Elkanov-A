"""
NOTE: There is no such a thing as jwt token for now - just a mocked is_auth status
"""

from data.core.mock_data import MOCK_ME_USER, MOCK_USERS


def get_user(request):
    if request.session.get("is_auth", False):
        return MOCK_ME_USER
    return None


def is_authenticated(request):
    return request.session.get("is_auth", False)


def login(request):
    request.session["is_auth"] = True
    request.session["user"] = MOCK_ME_USER


def logout(request):
    request.session["is_auth"] = False
    request.session.pop("user", None)


def get_all_mock_users():
    return MOCK_USERS
