from django.views import generic
from django.shortcuts import render, redirect
from django.db.models import Q, Prefetch
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
    paginate_by = 6

    def get_queryset(self):
        tag_slug = self.kwargs.get('slug')
        if tag_slug:
            queryset = Post.active_objs.filter(tags__slug=tag_slug)

        else:
            queryset = Post.active_objs.all()

        optimize_queryset = queryset.prefetch_related(Prefetch(
            'post_comments',
            queryset=PostComment.objects.filter(confirmation=True)
        )).order_by('-datetime_updated')

        return optimize_queryset


class PostSearchView(generic.ListView):
    model = Post
    context_object_name = 'posts'
    template_name = 'blog/search_page.html'
    paginate_by = 6

    def get_queryset(self):
        queryset = []
        request_get = self.request.GET

        if 'q' in request_get:
            form = PostSearchForm(request_get)
            if form.is_valid():
                q = form.cleaned_data['q']
                queryset = Post.active_objs.filter(
                    Q(title__icontains=q) | Q(tags__name__icontains=q)).distinct()

                queryset = queryset.prefetch_related(Prefetch(
                    'post_comments',
                    queryset=PostComment.objects.filter(confirmation=True)
                ))

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


@method_decorator(login_required, name='post')
class PostDetailView(generic.edit.FormMixin, generic.DetailView):
    model = Post
    form_class = PostCommentForm
    template_name = 'blog/post_detail.html'
    context_object_name = 'post'
    queryset = Post.active_objs.prefetch_related('tags', Prefetch(
        'post_comments',
        queryset=PostComment.objects.filter(confirmation=True)
    ))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = self.object

        if obj.tags.exists():
            context['next_previous_posts'] = Post.active_objs.filter(tags__in=obj.tags.all()).exclude(
                pk=obj.pk).order_by('datetime_updated').distinct()[0:2]

        else:
            context['next_previous_posts'] = Post.active_objs.exclude(pk=obj.pk).order_by(
                '-datetime_updated').distinct()[0:2]

        context['comments'] = PostComment.objects.filter(confirmation=True, post_id=obj.pk).select_related(
            'author__profile')

        return context

    def post(self, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        request = self.request

        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = self.object
            comment.author = request.user
            messages.success(request, _('You comment after confirmation will show in comments.'))
            comment.save()
            return redirect(self.object.get_absolute_url())
        else:
            messages.error(request, _('Your comment have problem please try again!'))
            return super().form_invalid(form)
