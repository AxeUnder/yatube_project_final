from django.contrib.auth.forms import (UserCreationForm,
                                       PasswordChangeForm,
                                       PasswordResetForm)

# from django import forms
# from .validators import validate_not_empty

from django.contrib.auth import get_user_model


User = get_user_model()


class CreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('first_name', 'last_name', 'username', 'email')


class ChangeForm(PasswordChangeForm):
    model = User
    fields = ('current_password', 'new_password', 'new_password_again')


class ResetForm(PasswordResetForm):
    model = User
    fields = ('email',)
