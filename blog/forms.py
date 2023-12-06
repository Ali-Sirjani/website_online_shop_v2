from django import forms

from .models import PostComment


class PostSearchForm(forms.Form):
    q = forms.CharField()


class PostCommentForm(forms.ModelForm):
    class Meta:
        model = PostComment
        fields = ('text',)
