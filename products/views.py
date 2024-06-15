from django.shortcuts import render
from . models import MainCategory, SubCategory, SubTypeCategory, Product, Cart, Order
from . serializers import MainCategorySerializer, SubCategorySerializer, SubTypeCategorySerializer, ProductSerializer, CartSerializer, OrderSerializer
from rest_framework import viewsets
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
import random
from rest_framework.pagination import PageNumberPagination
from django.utils import timezone
from datetime import timedelta
from rest_framework.decorators import action
from rest_framework import status


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

    def get_queryset(self):
        queryset = list(Product.objects.all())
        random.shuffle(queryset)
        return queryset
    
    def retrieve(self, request, pk=None):
        queryset = Product.objects.all()
        product = get_object_or_404(queryset, pk=pk)
        serializer = ProductSerializer(product, many=False)

        data = serializer.data
        data["image"] = request.build_absolute_uri(data["image"])

        return Response(data)

    
    @action(detail=False, methods=['get'])
    def new_arrivals(self, request):
        thirty_days_ago = timezone.now() - timedelta(days=3)
        queryset = list(Product.objects.filter(created_at__gte=thirty_days_ago))
        random.shuffle(queryset)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='main_category/(?P<main_category_id>[^/.]+)')
    def product_category(self, request, main_category_id=None):
        queryset = list(Product.objects.filter(main_category_id=main_category_id))
        random.shuffle(queryset)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
