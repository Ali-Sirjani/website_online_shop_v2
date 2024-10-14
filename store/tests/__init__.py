from .product_models_tests import (CategoryModelTest, ProductModelTest, ProductSpecificationModelTest,
                                   ProductSpecificationValueModelTest, ProductColorModelTest, ProductSizeModelTest,
                                   ProductColorAndSizeValueModelTest, ProductImageModelTest, TopProductModelTest,
                                   ProductCommentModelTest)
from .product_views_tests import (ProductsListViewTest, ProductSearchViewTest, ProductDetailViewTest, FavoriteViewTest,
                                  ProductUserLikedViewTest, FilterSizeBasedColorViewTest)
from .order_models_tests import (CouponModelTests, CouponRuleModelTests, OrderItemModelTests, OrderModelTests,
                                 ShippingAddressModelTests)
from .order_views_tests import (UpdateItemViewTest, CartViewTest, ApplyCouponViewTest, OrderDetailViewTest)
from .payment_views_tests import (CheckoutViewTest, )

