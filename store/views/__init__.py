from .product_views import (ProductsListView, ProductSearchView, ProductDetailView, favorite_view,
                            ProductUserLikedView, filter_size_based_color)
from .order_views import (update_color_size_drop, update_item, cart_view, OrderDetailView, apply_coupon_view)
from .payment_views import (checkout_view, set_profile_info, sandbox_process_payment, sandbox_callback_payment)
