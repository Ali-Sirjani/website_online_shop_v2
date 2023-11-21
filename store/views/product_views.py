from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.views import generic
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.db.models import Q, Max
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin

from django_filters.views import FilterMixin
import json

from ..models import Product, ProductComment, TopProduct
from ..utils import sort_product_queryset, optimize_product_query
from ..filters import ProductFilter
from ..forms import ProductCommentForm, SearchForm


class HomePageView(generic.ListView):
    template_name = 'store/product/home_page.html'
    context_object_name = 'top_products'

    def get_queryset(self):
        top_product_pk_list = TopProduct.active_objs.values_list('pk')
        product_queryset = Product.active_objs.filter(top_products__in=top_product_pk_list)

        product_queryset = optimize_product_query(product_queryset)

        product_queryset = product_queryset.order_by('top_products__level', '-top_products__is_top_level')

        return product_queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['liked'] = Product.active_objs.filter(favorite=self.request.user.pk).values_list('pk', flat=True)

        random_queryset = Product.active_objs.exclude(
            pk__in=self.get_queryset().values_list('pk')).order_by('?')

        context['random_products'] = optimize_product_query(random_queryset)[:5]
        return context


class ProductsListView(FilterMixin, generic.ListView):
    filterset_class = ProductFilter
    template_name = 'store/product/product_list.html'
    context_object_name = 'products'
    paginate_by = 2

    def get_queryset(self):
        queryset = Product.active_objs.all()

        queryset = optimize_product_query(queryset)

        sort_num = self.request.GET.get('sort')
        if sort_num:
            queryset = sort_product_queryset(sort_num, queryset)

        queryset = self.filterset_class(self.request.GET, queryset=queryset).qs
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = self.get_filterset(self.filterset_class)
        if self.request.user.is_authenticated:
            context['liked'] = Product.active_objs.filter(favorite=self.request.user.pk).values_list('pk', flat=True)
        sort_num = self.request.GET.get('sort')
        if sort_num:
            context['sort'] = f'&sort={sort_num}'
        return context


class CategoryView(ProductsListView):

    def get_queryset(self):
        queryset = Product.active_objs.filter(category__name=self.kwargs['slug'])

        queryset = optimize_product_query(queryset)

        sort_num = self.request.GET.get('sort')

        if sort_num:
            queryset = sort_product_queryset(sort_num, queryset)

        queryset = self.filterset_class(self.request.GET, queryset=queryset).qs

        return queryset


class ProductSearchView(ProductsListView):
    template_name = 'store/product/search_page.html'

    def get_queryset(self):
        queryset = []
        request_get = self.request.GET

        if 'q' in request_get:
            form = SearchForm(request_get)
            if form.is_valid():
                q = form.cleaned_data['q']
                queryset = Product.active_objs.filter(
                    Q(title__icontains=q) | Q(category__name__icontains=q)).distinct()

                queryset = optimize_product_query(queryset)

                self.q = q

                sort_num = self.request.GET.get('sort')
                if sort_num:
                    queryset = sort_product_queryset(sort_num, queryset)

        queryset = self.filterset_class(self.request.GET, queryset=queryset).qs

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
            return render(self.request, 'store/product/search_q_none.html')
        return super().dispatch(request, *args, **kwargs)


@method_decorator(login_required, name='post')
class ProductDetailView(generic.edit.FormMixin, generic.DetailView):
    model = Product
    form_class = ProductCommentForm
    template_name = 'store/product/product_detail.html'
    context_object_name = 'product'
    queryset = optimize_product_query(Product.active_objs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = self.object

        max_level_category = obj.category.all().aggregate(Max('level'))['level__max']
        category_pk_list = obj.category.filter(level=max_level_category).values_list('pk')

        related_product = self.get_queryset().filter(
            category__in=category_pk_list,
        ).exclude(pk=obj.pk).order_by('?')
        context['related_products'] = related_product[:8]

        if self.request.user.is_authenticated:
            context['liked'] = Product.active_objs.filter(favorite=self.request.user.pk).values_list('pk', flat=True)

        context['comments'] = ProductComment.objects.filter(confirmation=True, product=self.object.pk).select_related(
            'author')
        return context

    def post(self, *args, **kwargs):
        obj = self.get_object()
        form = self.get_form()
        request = self.request

        if form.is_valid():
            comment = form.save(commit=False)
            comment.product = get_object_or_404(Product, pk=obj.pk)
            comment.author = request.user
            messages.success(request, _('You comment after confirmation will show in comments.'))
            comment.save()
            return redirect(obj.get_absolute_url())
        else:
            messages.error(request, _('Your comment have problem please try again!'))
            return super().form_invalid(form)


@require_POST
def favorite_view(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        messages.warning(request, _('Oops! Something went wrong with your request. Please try again.'
                                    ' If the issue persists, contact our support team for assistance.'))
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    if request.user.is_authenticated:
        pk = data.get('productId')
        product_obj = get_object_or_404(Product.active_objs, pk=pk,)
        user = request.user
        if product_obj.favorite.filter(pk=user.pk).exists():
            product_obj.favorite.remove(user)
            messages.error(request, _('Unlike post.'))
        else:
            product_obj.favorite.add(user)
            messages.success(request, _('Like post.'))

        response = {'authenticated': True}
        return JsonResponse(response, safe=False)
    else:
        messages.info(request, _('Please first login!'))
        response = {'authenticated': False, 'login': request.build_absolute_uri(reverse('account_login'))}
        return JsonResponse(response, safe=False)


class ProductUserLikedView(LoginRequiredMixin, ProductsListView):
    filterset_class = ProductFilter
    template_name = 'store/product/product_list_user_like.html'
    context_object_name = 'products'
    paginate_by = 2

    def get_queryset(self):
        queryset = Product.active_objs.filter(favorite=self.request.user)

        queryset = optimize_product_query(queryset)

        sort_num = self.request.GET.get('sort')
        if sort_num:
            queryset = sort_product_queryset(sort_num, queryset)

        queryset = self.filterset_class(self.request.GET, queryset=queryset).qs
        return queryset
