from django.shortcuts import get_object_or_404
from rest_framework import generics, viewsets, status, filters
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import FormParser, MultiPartParser
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q
import random
import traceback

from .models import MainCategory, SubCategory, SubTypeCategory, Product, Cart, Order
from .serializers import (
    MainCategorySerializer, SubCategorySerializer, SubTypeCategorySerializer,
    ProductSerializer, CartSerializer, OrderSerializer, CreateProductSerializer
)
from .permissions import IsSellerOrReadOnly
from rest_framework.views import APIView
from django_daraja.mpesa.core import MpesaClient


# Pagination class for consistent pagination
class ProductPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 100


# MainCategory Viewset
class MainCategoryView(viewsets.ModelViewSet):
    queryset = MainCategory.objects.all()
    serializer_class = MainCategorySerializer
    parser_classes = [FormParser, MultiPartParser]
    pagination_class = ProductPagination


# SubCategory Viewset
class SubCategoryView(viewsets.ModelViewSet):
    queryset = SubCategory.objects.all()
    serializer_class = SubCategorySerializer
    parser_classes = [FormParser, MultiPartParser]
    pagination_class = ProductPagination


# SubTypeCategory Viewset
class SubTypeCategoryView(viewsets.ModelViewSet):
    queryset = SubTypeCategory.objects.all()
    serializer_class = SubTypeCategorySerializer
    parser_classes = [FormParser, MultiPartParser]
    pagination_class = ProductPagination


# Product Viewset
class ProductView(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsSellerOrReadOnly]
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

        # Filter for logged-in seller's products if applicable
        if self.request.user.is_authenticated and self.request.user.is_seller:
            queryset = queryset.filter(seller=self.request.user)

        return queryset

    def perform_create(self, serializer):
        # Associate the logged-in user as the seller
        serializer.save(seller=self.request.user)

    def perform_update(self, serializer):
        serializer.save()

    def create(self, request, *args, **kwargs):
        # Custom logic for creating products with categories
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
        data['seller'] = request.user.id  # Associate seller

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=False, methods=['get'], url_path='search')
    def search(self, request):
        # Search functionality for products
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
        # Filter products added in the last 30 days
        thirty_days_ago = timezone.now() - timedelta(days=30)
        queryset = list(Product.objects.filter(created_at__gte=thirty_days_ago))
        random.shuffle(queryset)  # Randomize the order of new arrivals

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='category/(?P<main_category_id>[^/.]+)')
    def product_category(self, request, main_category_id=None):
        """
        Retrieve all products filtered by the main category.
        """
        # Fetch the main category using the provided main_category_id
        main_category = get_object_or_404(MainCategory, id=main_category_id)
        
        # Filter products that belong to the specified main category
        products = Product.objects.filter(main_category=main_category)
        
        # Apply pagination if needed
        page = self.paginate_queryset(products)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        # Serialize the filtered products
        serializer = ProductSerializer(products, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


# Cart Viewset
class CartView(viewsets.ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Show only the current user's cart
        return Cart.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Ensure the logged-in user is associated with the cart
        serializer.save(user=self.request.user)


# Order Viewset
class OrderView(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        # Link the order to the logged-in user
        order = serializer.save(user=self.request.user)

        # After payment confirmation, reduce product quantities
        for item in order.orderitem_set.all():
            item.product.quantity -= item.quantity
            item.product.save()



# Payment View
class PaymentView(APIView):
    def post(self, request):
        try:
            phone_number = request.data.get("phone_number")
            amount = request.data.get("price")

            if not phone_number or not amount:
                return Response(
                    {"error": "Phone number and amount are required."}, status=400
                )

            # MpesaClient initialization (sample logic)
            cl = MpesaClient()
            token = cl.access_token()
            account_reference = "reference"
            transaction_desc = "Description"
            callback_url = "https://api.darajambili.com/express-payment"
            response = cl.stk_push(
                phone_number, amount, account_reference, transaction_desc, callback_url
            )

            # After successful payment, adjust product quantities
            if response['ResponseCode'] == '0':  # Payment success
                order = Order.objects.get(id=request.data.get("order_id"))
                for item in order.orderitem_set.all():
                    item.product.quantity -= item.quantity
                    item.product.save()

            return Response(response)
        except Exception as e:
            traceback.print_exc()
            return Response({"error": str(e)}, status=500)
