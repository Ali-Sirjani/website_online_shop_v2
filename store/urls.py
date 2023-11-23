from django.urls import path, re_path

from . import views

app_name = 'store'

urlpatterns = [
    path('home', views.HomePageView.as_view(), name='home_page'),
    path('list/', views.ProductsListView.as_view(), name='product_list'),
    path('search/', views.ProductSearchView.as_view(), name='product_search'),
    path('favorite/', views.favorite_view, name='set_favorite_product'),
    path('favorite/list/', views.ProductUserLikedView.as_view(), name='favorite_product_list'),
    re_path(r'list/category/(?P<slug>[-\w]+)/', views.ProductsListView.as_view(), name='category_page'),
    re_path(r'(?P<slug>[-\w]+)/', views.ProductDetailView.as_view(), name='product_detail'),
]
