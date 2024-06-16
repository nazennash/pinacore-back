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
from rest_framework.permissions import IsAuthenticated
import traceback
from django_daraja.mpesa.core import MpesaClient
from rest_framework.views import APIView
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q


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
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description', 'main_category__name', 'sub_category__name']
    ordering_fields = ['name', 'price', 'created_at']

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
    
    @action(detail=False, methods=['get'], url_path='search')
    def search(self, request):
        q = request.query_params.get('search', '')
        queryset = Product.objects.filter(
            Q(name__icontains=q) |
            Q(description__icontains=q) |
            Q(main_category__name__icontains=q) |
            Q(sub_category__name__icontains=q) |
            Q(sub_type_category__name__icontains=q) 
        )

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    
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
    
class OrderView(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

class PaymentView(APIView):
    def post(self, request):
        try:
            print(request.user)
            phone_number = request.data.get("phone_number")
            print(phone_number)
            amount = request.data.get("price")
            print(amount)

            if not phone_number or not amount:
                return Response(
                    {"error": "Phone number and amount are required."}, status=400
                )

            print("one")
            cl = MpesaClient()
            token = cl.access_token()
            account_reference = "reference"
            transaction_desc = "Description"
            print("two")
            callback_url = (
                "https://api.darajambili.com/express-payment" 
            )
            print("three")
            response = cl.stk_push(
                phone_number, amount, account_reference, transaction_desc, callback_url
            )
            print("four")

            return Response(response)
        except Exception as e:
            traceback.print_exc()
            return Response({"error": str(e)}, status=500)
