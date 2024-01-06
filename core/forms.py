from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, UsernameField
from django.utils.translation import gettext_lazy as _

from .models import Profile, ContactUs, ProfileAddress


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
        fields = ('first_name', 'last_name', 'phone', 'picture')
        widgets = {'picture': forms.FileInput}


class ProfileAddressFrom(forms.ModelForm):
    class Meta:
        model = ProfileAddress
        fields = ('state', 'city', 'address', 'plate')


class SetUsernameForm(forms.Form):
    username = forms.CharField(max_length=150, label=_('username'))


class ContactUsForm(forms.ModelForm):
    class Meta:
        model = ContactUs
        fields = ('full_name', 'email', 'phone', 'message')

    def clean(self):
        clean_data = super().clean()
        if self.is_valid():

            email = clean_data.get('email')
            phone = clean_data.get('phone')

            if not (email or phone):
                self.add_error(None, _('You must fill email or phone'))

        return clean_data
