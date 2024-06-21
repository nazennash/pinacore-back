from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('main_category', views.MainCategoryView, basename='main_category')
router.register('sub_category', views.SubCategoryView, basename='sub_category')
router.register('sub_type_category', views.SubTypeCategorView, basename='sub_type_category')
router.register('products', views.ProductView, basename='products')
router.register('order', views.OrderView, basename='order')

urlpatterns = [
    path('', include(router.urls)),
    path('create_new/', views.CreateProductCreateView.as_view(), name='product-create'),
    path("payment/", views.PaymentView.as_view(), name="payment"),

] 