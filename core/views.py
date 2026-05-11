from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View
from django.utils.http import url_has_allowed_host_and_scheme

from core.forms import LoginForm, ProfileForm, SignupForm


def handler400(request, exception):
    return render(request, "errors/400.html", status=400)


def handler403(request, exception):
    return render(request, "errors/403.html", status=403)


def handler404(request, exception):
    return render(request, "errors/404.html", status=404)


def handler500(request):
    return render(request, "errors/500.html", status=500)


class LoginView(View):
    template_name = "core/login.html"

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("/")
        form = LoginForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request, *args, **kwargs):
        form = LoginForm(request.POST)
        if form.is_valid():
            user = form.user
            login(request, user)
            next_url = request.GET.get("next") or request.POST.get("next")
            if next_url and url_has_allowed_host_and_scheme(
                url=next_url, allowed_hosts={request.get_host()}
            ):
                return redirect(next_url)
            return redirect("/")
        return render(request, self.template_name, {"form": form})


class SignupView(View):
    template_name = "core/signup.html"

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("/")
        form = SignupForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request, *args, **kwargs):
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("/")
        return render(request, self.template_name, {"form": form})


class LogoutView(View):
    def post(self, request, *args, **kwargs):
        logout(request)
        next_url = request.META.get("HTTP_REFERER", "/")
        if next_url and url_has_allowed_host_and_scheme(
            url=next_url, allowed_hosts={request.get_host()}
        ):
            return redirect(next_url)
        return redirect("/")

    def get(self, request, *args, **kwargs):
        logout(request)
        next_url = request.META.get("HTTP_REFERER", "/")
        if next_url and url_has_allowed_host_and_scheme(
            url=next_url, allowed_hosts={request.get_host()}
        ):
            return redirect(next_url)
        return redirect("/")


class ProfileView(LoginRequiredMixin, View):
    template_name = "core/profile.html"
    login_url = "core:login"

    def get(self, request, *args, **kwargs):
        form = ProfileForm(instance=request.user)
        return render(request, self.template_name, {"form": form})

    def post(self, request, *args, **kwargs):
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect("core:profile")
        return render(request, self.template_name, {"form": form})
