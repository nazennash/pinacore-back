from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Define the router
router = DefaultRouter()

# Register routes for the viewsets
router.register('main_category', views.MainCategoryView, basename='main_category')
router.register('sub_category', views.SubCategoryView, basename='sub_category')
router.register('sub_type_category', views.SubTypeCategoryView, basename='sub_type_category')
router.register('products', views.ProductView, basename='products')
router.register('cart', views.CartView, basename='cart')
router.register('order', views.OrderView, basename='order')

# URL Patterns
urlpatterns = [
    path('', include(router.urls)),  # Include the router-generated URLs
    # path('create_new/', views.CreateProductCreateView.as_view(), name='product-create'),  # Custom product creation endpoint
    path("payment/", views.PaymentView.as_view(), name="payment"),  # Payment processing endpoint
]
