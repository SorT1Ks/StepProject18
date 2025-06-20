from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(label='Електронна пошта', help_text='Введіть вашу email адресу')

    username = forms.CharField(
        label='Логін',
        help_text='Використовуйте лише букви, цифри та @/./+/-/_',
        error_messages={
            'required': 'Це поле обовʼязкове.',
            'max_length': 'Максимальна довжина — 150 символів.',
            'invalid': 'Використовуйте лише букви, цифри та @/./+/-/_',
        }
    )

    password1 = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput,
        help_text=(
            'Ваш пароль має містити щонайменше 8 символів.<br>'
            'Не використовуйте занадто прості або популярні паролі.<br>'
            'Не можна використовувати лише цифри.'
        ),
    )

    password2 = forms.CharField(
        label='Підтвердіть пароль',
        widget=forms.PasswordInput,
        help_text='Введіть той самий пароль ще раз для підтвердження.'
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']