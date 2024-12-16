from django import forms
from .models import UserProfile


class UserRegisterForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['username', 'email', 'password', 'first_name', 'last_name']

    password = forms.CharField(widget=forms.PasswordInput)  # Пароль с защитой

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if password:
            return make_password(password)  # Хэшируем пароль
        return password
