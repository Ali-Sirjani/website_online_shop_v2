from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, UsernameField

from .models import Profile


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = ('username', 'email')
        field_classes = {'username': UsernameField}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.get('email').required = True
        self.fields.get('username').required = False

    def clean(self):
        clean_data = super().clean()
        username = clean_data.get('username')
        email = clean_data.get('email')

        if username == '':
            if email:
                username_based_email = email.split('@')[0]
                clean_data['username'] = username_based_email

        return clean_data


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = get_user_model()
        fields = UserChangeForm.Meta.fields


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('first_name', 'last_name', 'phone', 'picture', 'state', 'city', 'address', 'plate')
        widgets = {'picture': forms.FileInput}
