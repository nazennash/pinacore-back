from django.shortcuts import render
from . models import MainCategory, SubCategory, SubTypeCategory, Product, Cart, Order
from . serializers import MainCategorySerializer, SubCategorySerializer, SubTypeCategorySerializer, ProductSerializer, CartSerializer, OrderSerializer, CreateProductSerializer
from rest_framework import generics

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
from rest_framework.parsers import  FormParser, MultiPartParser


class ProductPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 100


class MainCategoryView(viewsets.ModelViewSet):
    queryset = MainCategory.objects.all()
    serializer_class = MainCategorySerializer
    parser_classes = [FormParser, MultiPartParser] 
    
    
class SubCategoryView(viewsets.ModelViewSet):
    queryset = SubCategory.objects.all()
    serializer_class = SubCategorySerializer
    parser_classes = [FormParser, MultiPartParser] 

class SubTypeCategorView(viewsets.ModelViewSet):
    queryset = SubTypeCategory.objects.all()
    serializer_class = SubTypeCategorySerializer
    parser_classes = [FormParser, MultiPartParser] 

class CreateProductCreateView(generics.CreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def perform_create(self, serializer):
        
        instance = serializer.save()

        print(f"Created product: {instance}")
        print(f"Product details: {serializer.data}")



from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import FormParser, MultiPartParser
from django_filters.rest_framework import DjangoFilterBackend
from .models import Product, MainCategory, SubCategory, SubTypeCategory
from .serializers import ProductSerializer
from .permissions import IsSellerOrReadOnly
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from django.db.models import Q
import random
from datetime import timedelta
from django.utils import timezone

class ProductPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 100

class ProductView(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsSellerOrReadOnly]  # Apply custom permission
    parser_classes = [FormParser, MultiPartParser]
    pagination_class = ProductPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description', 'main_category__name', 'sub_category__name']
    ordering_fields = ['name', 'price', 'created_at']

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Handle filtering by seller
        seller_username = self.request.query_params.get('seller', None)
        
        if seller_username:
            queryset = queryset.filter(seller__username=seller_username)
        
        # Further filter to the products of the logged-in seller if the user is authenticated and a seller
        if self.request.user.is_authenticated and self.request.user.is_seller:
            queryset = queryset.filter(seller=self.request.user)
        
        return queryset

    def perform_create(self, serializer):
        # Automatically associate the logged-in user as the seller
        serializer.save(seller=self.request.user)

    def perform_update(self, serializer):
        serializer.save()

    def create(self, request, *args, **kwargs):
        main_category_id = request.data.get('main_category')
        sub_category_id = request.data.get('sub_category')
        sub_type_category_id = request.data.get('sub_type_category')

        try:
            main_category = MainCategory.objects.get(id=main_category_id)
        except MainCategory.DoesNotExist:
            return Response({'main_category': 'MainCategory does not exist'}, status=status.HTTP_404_NOT_FOUND)

        try:
            sub_category = SubCategory.objects.get(id=sub_category_id)
        except SubCategory.DoesNotExist:
            return Response({'sub_category': 'SubCategory does not exist'}, status=status.HTTP_404_NOT_FOUND)

        try:
            sub_type_category = SubTypeCategory.objects.get(id=sub_type_category_id)
        except SubTypeCategory.DoesNotExist:
            return Response({'sub_type_category': 'SubTypeCategory does not exist'}, status=status.HTTP_404_NOT_FOUND)

        data = request.data.copy()
        data['main_category'] = main_category.id
        data['sub_category'] = sub_category.id
        data['sub_type_category'] = sub_type_category.id
        data['seller'] = request.user.id  # Automatically associate the seller

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        main_category_id = request.data.get('main_category')
        sub_category_id = request.data.get('sub_category')
        sub_type_category_id = request.data.get('sub_type_category')

        try:
            main_category = MainCategory.objects.get(id=main_category_id)
        except MainCategory.DoesNotExist:
            return Response({'main_category': 'MainCategory does not exist'}, status=status.HTTP_404_NOT_FOUND)

        try:
            sub_category = SubCategory.objects.get(id=sub_category_id)
        except SubCategory.DoesNotExist:
            return Response({'sub_category': 'SubCategory does not exist'}, status=status.HTTP_404_NOT_FOUND)

        try:
            sub_type_category = SubTypeCategory.objects.get(id=sub_type_category_id)
        except SubTypeCategory.DoesNotExist:
            return Response({'sub_type_category': 'SubTypeCategory does not exist'}, status=status.HTTP_404_NOT_FOUND)

        data = request.data.copy()
        data['main_category'] = main_category.id
        data['sub_category'] = sub_category.id
        data['sub_type_category'] = sub_type_category.id

        serializer = self.get_serializer(instance, data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        queryset = self.get_queryset()
        product = get_object_or_404(queryset, pk=pk)
        serializer = ProductSerializer(product, many=False)
        data = serializer.data
        data["image"] = request.build_absolute_uri(data["image"])
        return Response(data)

    @action(detail=False, methods=['post'], url_path='create')
    def add(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=True, methods=['put'], url_path='upload-image')
    def upload_image(self, request, pk=None):
        product = self.get_object()
        serializer = ProductSerializer(product, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='search')
    def search(self, request):
        q = request.query_params.get('search', '')
        queryset = Product.objects.filter(
            Q(name__icontains=q) |
            Q(description__icontains(q)) |
            Q(main_category__name__icontains(q)) |
            Q(sub_category__name__icontains(q)) |
            Q(sub_type_category__name__icontains(q))
        )

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def new_arrivals(self, request):
        thirty_days_ago = timezone.now() - timedelta(days=30)
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
