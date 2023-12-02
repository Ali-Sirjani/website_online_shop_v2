from django.urls import path, re_path

from . import views

app_name = 'store'

urlpatterns = [
    path('list/', views.ProductsListView.as_view(), name='product_list'),
    path('search/', views.ProductSearchView.as_view(), name='product_search'),
    path('favorite/', views.favorite_view, name='set_favorite_product'),
    path('favorite/list/', views.ProductUserLikedView.as_view(), name='favorite_product_list'),
    path('cart/', views.cart_view, name='cart_page'),
    path('cart/update-item/', views.update_item, name='update_item'),
    path('admin-drop/color-size/', views.update_color_size_drop, name='color_size_drop'),
    re_path(r'list/category/(?P<slug>[-\w]+)/', views.ProductsListView.as_view(), name='category_page'),
    re_path(r'(?P<slug>[-\w]+)/', views.ProductDetailView.as_view(), name='product_detail'),
]
