from django.urls import path, re_path

from . import views

app_name = 'store'

urlpatterns = [
    path('', views.ProductsListView.as_view(), name='product_list'),
    path('search/', views.ProductSearchView.as_view(), name='product_search'),
    path('favorite/', views.favorite_view, name='set_favorite_product'),
    re_path(r'category/(?P<slug>[-\w]+)/', views.CategoryView.as_view(), name='category_page'),
    re_path(r'(?P<slug>[-\w]+)/', views.ProductDetailView.as_view(), name='product_detail'),
]
