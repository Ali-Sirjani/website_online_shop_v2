from django.db.models import Prefetch

from .models import Tag, TopTag, Post, PostComment


def top_tag_list(request):
    top_tag_pk_list = TopTag.objects.values_list('pk')
    tag_queryset = Tag.objects.filter(top_tags__in=top_tag_pk_list)

    tag_queryset = tag_queryset.order_by('top_tags__level', '-top_tags__is_top_level')

    context = {'top_tags': tag_queryset}

    return context


def recent_posts(request):
    post_query = Post.active_objs.all().prefetch_related(Prefetch(
        'post_comments',
        queryset=PostComment.objects.filter(confirmation=True)
    )).order_by('-datetime_created')[0:4]

    context = {'recent_posts': post_query}

    return context
