from django.shortcuts import render
from . models import MainCategory, SubCategory, SubTypeCategory, Product, Cart, Order
from . serializers import MainCategorySerializer, SubCategorySerializer, SubTypeCategorySerializer, ProductSerializer, CartSerializer, OrderSerializer
from rest_framework import viewsets
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
import random
from rest_framework.pagination import PageNumberPagination


class ProductPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 100


class MainCategoryView(viewsets.ModelViewSet):
    queryset = MainCategory.objects.all()
    serializer_class = MainCategorySerializer
    
class SubCategoryView(viewsets.ModelViewSet):
    queryset = SubCategory.objects.all()
    serializer_class = SubCategorySerializer

class SubTypeCategorView(viewsets.ModelViewSet):
    queryset = SubTypeCategory.objects.all()
    serializer_class = SubTypeCategorySerializer

class ProductView(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    pagination_class = ProductPagination