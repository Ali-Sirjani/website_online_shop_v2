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


class PostSearchView(generic.ListView):
    model = Post
    context_object_name = 'posts'
    template_name = 'blog/search_page.html'
    paginate_by = 3

    def get_queryset(self):
        queryset = []
        request_get = self.request.GET

        if 'q' in request_get:
            form = PostSearchForm(request_get)
            if form.is_valid():
                q = form.cleaned_data['q']
                queryset = Post.active_objs.filter(
                    Q(title__icontains=q) | Q(tags__name__icontains=q)).distinct()

                queryset = queryset.prefetch_related('tags')
                self.q = q

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['q'] = self.q
        except AttributeError:
            context['q'] = None
        return context

    def dispatch(self, request, *args, **kwargs):
        q = request.GET.get('q')
        if not q or q.isspace():
            return render(self.request, 'blog/search_q_none.html')
        return super().dispatch(request, *args, **kwargs)
