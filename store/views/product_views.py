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

from ..models import Product, ProductComment, Category, ProductColorAndSizeValue
from ..utils import sort_product_queryset, optimize_product_query
from ..filters import ProductFilter
from ..forms import ProductCommentForm, SearchForm


class ProductsListView(FilterMixin, generic.ListView):
    filterset_class = ProductFilter
    template_name = 'store/product/product_list.html'
    context_object_name = 'products'
    paginate_by = 9

    def get_queryset(self):
        category_slug = self.kwargs.get('slug')
        if category_slug:
            category_obj = get_object_or_404(Category, slug=category_slug)
            category_descendants = category_obj.get_descendants(True)
            queryset = Product.active_objs.filter(category__in=category_descendants).distinct()

        else:
            queryset = Product.active_objs.all()
        queryset = optimize_product_query(queryset.order_by('-datetime_updated'))

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

        category_slug = self.kwargs.get('slug')
        if category_slug:
            context['category'] = get_object_or_404(Category, slug=category_slug)

        return context


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

                queryset = optimize_product_query(queryset.order_by('-datetime_updated'))

                if queryset.exists():
                    self.empty_query = False
                else:
                    self.empty_query = True

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

        try:
            context['empty_query'] = self.empty_query
        except AttributeError:
            context['empty_query'] = False

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
        ).exclude(pk=obj.pk).order_by('?').distinct()
        context['related_products'] = related_product[:8]

        if self.request.user.is_authenticated:
            context['liked'] = Product.active_objs.filter(favorite=self.request.user.pk).values_list('pk', flat=True)

        context['comments'] = ProductComment.objects.filter(confirmation=True, product=self.object.pk).select_related(
            'author__profile').order_by('-datetime_updated')
        return context

    def post(self, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        request = self.request

        if form.is_valid():
            comment = form.save(commit=False)
            comment.product = self.object
            comment.author = request.user
            messages.success(request, _('You comment after confirmation will show in comments.'))
            comment.save()
            return redirect(self.object.get_absolute_url())
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
        product_obj = get_object_or_404(Product.active_objs, pk=pk, )
        user = request.user
        if product_obj.favorite.filter(pk=user.pk).exists():
            product_obj.favorite.remove(user)
            messages.error(request, _('Unlike product.'))
        else:
            product_obj.favorite.add(user)
            messages.success(request, _('Like product.'))

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

    def get_queryset(self):
        queryset = Product.active_objs.filter(favorite=self.request.user)

        queryset = optimize_product_query(queryset)

        sort_num = self.request.GET.get('sort')
        if sort_num:
            queryset = sort_product_queryset(sort_num, queryset)

        queryset = self.filterset_class(self.request.GET, queryset=queryset).qs
        return queryset


def filter_size_based_color(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        messages.warning(request, _('Oops! Something went wrong with your request. Please try again.'
                                    ' If the issue persists, contact our support team for assistance.'))
        return JsonResponse('Something went wrong', safe=False)

    product_pk = data.get('productId')
    color_pk = data.get('colorId')

    if not (color_pk or product_pk):
        messages.warning(request, _('Something went wrong with your request.'))
        return JsonResponse('Something went wrong', safe=False)

    color_size_query = ProductColorAndSizeValue.active_objs.filter(product_id=product_pk, color_id=color_pk)

    size_pk_set = set()

    for color_size in color_size_query:
        if color_size.size:
            size_pk_set.add(str(color_size.size.pk))

    size_pk_list = list(size_pk_set)

    data_response = {'sizeIds': size_pk_list}
    return JsonResponse(data_response, safe=False)
