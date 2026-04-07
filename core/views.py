from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from .auth import get_user, is_authenticated, login, logout


@csrf_exempt
def login_view(request):
    if is_authenticated(request):
        return redirect("questions:index")

    if request.method == "POST":
        login(request)
        return redirect("questions:index")

    return render(
        request,
        "core/login.html",
    )


@csrf_exempt
def signup_view(request):
    if is_authenticated(request):
        return redirect("questions:index")

    if request.method == "POST":
        login(request)
        return redirect("questions:index")

    return render(
        request,
        "core/signup.html",
    )


@csrf_exempt
@require_POST
def logout_view(request):
    logout(request)
    return redirect("core:login")


def profile_view(request):
    user = get_user(request)

    if not user:
        return redirect("core:login")

    return render(
        request,
        "core/profile.html",
        {
            "user": user,
        },
    )
