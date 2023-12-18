from django import forms
from django.utils.translation import gettext_lazy as _

from .models import PostComment


class PostSearchForm(forms.Form):
    q = forms.CharField()


class PostCommentForm(forms.ModelForm):
    class Meta:
        model = PostComment
        fields = ('text',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        text_field = self.fields.get('text')
        if text_field:
            text_field.widget.attrs['class'] = 'mb-0 input-info-save'
            text_field.widget.attrs['placeholder'] = _('Type your comments....')
