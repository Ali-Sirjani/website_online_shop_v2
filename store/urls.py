from django.urls import path, re_path
from django.views.generic import TemplateView

from . import views

app_name = 'store'

urlpatterns = [
    path('list/', views.ProductsListView.as_view(), name='product_list'),
    path('search/', views.ProductSearchView.as_view(), name='product_search'),
    path('filter-size/', views.filter_size_based_color, name='filter_size_ajax'),
    path('favorite/', views.favorite_view, name='set_favorite_product'),
    path('favorite/list/', views.ProductUserLikedView.as_view(), name='favorite_product_list'),
    path('cart/', views.cart_view, name='cart_page'),
    path('cart/update-item/', views.update_item, name='update_item'),
    path('apply-coupon/', views.apply_coupon_view, name='apply_coupon'),
    path('order/<int:pk>/', views.OrderDetailView.as_view(), name='order_detail'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('process/checkout/', views.sandbox_process_payment, name='sandbox_process'),
    path('process/callback/', views.sandbox_callback_payment, name='sandbox_callback'),
    path('checkout/success/', TemplateView.as_view(template_name='store/payment/success.html')),
    path('checkout/fail/', TemplateView.as_view(template_name='store/payment/fail.html')),
    path('checkout/again/', TemplateView.as_view(template_name='store/payment/again.html')),
    path('admin-drop/color-size/', views.update_color_size_drop, name='color_size_drop'),
    re_path(r'list/category/(?P<slug>[-\w]+)/', views.ProductsListView.as_view(), name='category_page'),
    re_path(r'(?P<slug>[-\w]+)/', views.ProductDetailView.as_view(), name='product_detail'),
]
