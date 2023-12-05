from django.views import generic
from django.shortcuts import render, redirect
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _

from .models import Post, PostComment
from .forms import PostSearchForm, PostCommentForm


class PostListView(generic.ListView):
    model = Post
    context_object_name = 'posts'
    template_name = 'blog/post_list.html'
    paginate_by = 2

    def get_queryset(self):
        tag_slug = self.kwargs.get('slug')
        if tag_slug:
            queryset = Post.active_objs.filter(tags__slug=tag_slug)

        else:
            queryset = Post.active_objs.all()

        optimize_queryset = queryset.prefetch_related('tags')

        return optimize_queryset
