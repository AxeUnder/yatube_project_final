# users/views.py

from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail

from .forms import CreationForm, ResetForm, ChangeForm
# from django.shortcuts import render, redirect


""""
def authorized_only(func):
    # Функция-обёртка в декораторе может быть названа как угодно
    def check_user(request, *args, **kwargs):
        # В любую view-функцию первым аргументом передаётся объект request,
        # в котором есть булева переменная is_authenticated,
        # определяющая, авторизован ли пользователь.
        if request.user.is_authenticated:
            # Возвращает view-функцию, если пользователь авторизован.
            return func(request, *args, **kwargs)
        # Если пользователь не авторизован — отправим его на страницу логина.
        return redirect('/auth/login/')
    return check_user
"""


class SignUp(CreateView):
    form_class = CreationForm
    success_url = reverse_lazy('posts:index')
    template_name = 'users/signup.html'


class PasswordReset(CreateView):
    form_clas = ResetForm
    success_url = reverse_lazy('users:password_reset_done')
    template_name = 'users/password_reset_form.html'


@login_required
class PasswordChange(CreateView):
    form_class = ChangeForm
    success_url = reverse_lazy('users:password_change_done')
    template_name = 'users/password_change_form.html'


def send_msg(email, name, subject, body, is_answered):
    subject = f"{name}-{subject}"
    body = f"""Письмо от {name} ({email})
    Тема: {subject}
    Сообщение: {body}
    Ответ получен: {is_answered}
    """
    send_mail(
        subject, body, email, ["admin@rockenrolla.net", ],
    )
