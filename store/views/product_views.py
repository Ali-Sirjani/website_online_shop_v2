from django.shortcuts import get_object_or_404, redirect, render
from django.views import generic
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.db.models import Q, Prefetch

from django_filters.views import FilterMixin

from ..models import Product, ProductSpecificationValue, ProductColorAndSizeValue, ProductComment
from ..utils import sort_product_queryset
from ..filters import ProductFilter
from ..forms import ProductCommentForm, SearchForm


class ProductsListView(FilterMixin, generic.ListView):
    filterset_class = ProductFilter
    template_name = 'store/product/product_list.html'
    context_object_name = 'products'
    paginate_by = 2

    def get_queryset(self):
        queryset = Product.active_objs.all().prefetch_related(
            Prefetch(
                'specs_values',
                queryset=ProductSpecificationValue.objects.select_related('specification')
            ),
            Prefetch(
                'color_size_values',
                queryset=ProductColorAndSizeValue.objects.select_related('color', 'size')
            ),
            'images',
        )

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
        queryset = Product.active_objs.filter(category__name=self.kwargs['slug']).prefetch_related(
            Prefetch(
                'specs_values',
                queryset=ProductSpecificationValue.objects.select_related('specification')
            ),
            Prefetch(
                'color_size_values',
                queryset=ProductColorAndSizeValue.objects.select_related('color', 'size')
            ),
            'images',
        )

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

                queryset = queryset.prefetch_related(
                    Prefetch(
                        'specs_values',
                        queryset=ProductSpecificationValue.objects.select_related('specification')
                    ),
                    Prefetch(
                        'color_size_values',
                        queryset=ProductColorAndSizeValue.objects.select_related('color', 'size')
                    ),
                    'images',
                )
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
            return render(self.request, 'store/product/search_none.html')
        return super().dispatch(request, *args, **kwargs)


@method_decorator(login_required, name='post')
class ProductDetailView(generic.edit.FormMixin, generic.DetailView):
    model = Product
    form_class = ProductCommentForm
    template_name = 'store/product/product_detail.html'
    context_object_name = 'product'
    queryset = Product.active_objs.prefetch_related(
        Prefetch(
            'specs_values',
            queryset=ProductSpecificationValue.objects.select_related('specification')
        ),
        Prefetch(
            'color_size_values',
            queryset=ProductColorAndSizeValue.objects.select_related('color', 'size')
        ),
        'images',
    )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = ProductComment.objects.filter(confirmation=True, product=self.object.pk).select_related(
            'author')
        return context

    def post(self, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        request = self.request

        if form.is_valid():
            comment = form.save(commit=False)
            comment.product = get_object_or_404(Product, pk=self.object.pk)
            comment.author = request.user
            messages.success(request, _('You comment after confirmation will show in comments.'))
            comment.save()
            return redirect(self.object.get_absolute_url())
        else:
            messages.error(request, _('Your comment have problem please try again!'))
            return super().form_invalid(form)
