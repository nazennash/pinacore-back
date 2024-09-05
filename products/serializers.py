from rest_framework import serializers
from .models import MainCategory, SubCategory, SubTypeCategory, Product, Cart, Order, ProductImage

class MainCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = MainCategory
        fields = '__all__'

class SubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SubCategory
        fields = '__all__'

class SubTypeCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SubTypeCategory
        fields = '__all__'


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['image']

from rest_framework import serializers
from .models import MainCategory, SubCategory, SubTypeCategory, Product, ProductImage

class ProductSerializer(serializers.ModelSerializer):
    seller = serializers.ReadOnlyField(source='seller.username')
    main_category = serializers.PrimaryKeyRelatedField(queryset=MainCategory.objects.all())
    sub_category = serializers.PrimaryKeyRelatedField(queryset=SubCategory.objects.all())
    sub_type_category = serializers.PrimaryKeyRelatedField(queryset=SubTypeCategory.objects.all())
    images = serializers.SerializerMethodField()  # Custom field for image URLs
    discount_percentage = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'seller', 'main_category', 'sub_category', 'sub_type_category',
            'name', 'description', 'price', 'discounted_price', 'discount_percentage',
            'brand', 'size', 'color', 'quantity', 'created_at', 'updated_at', 'images'
        ]

    def get_images(self, obj):
        request = self.context.get('request')
        images = obj.images.all()
        
        # Check if there are images, otherwise return an empty list or a default image
        if images:
            return [request.build_absolute_uri(image.image.url) for image in images]
        return []  # You could also provide a default image URL if needed

    def get_discount_percentage(self, obj):
        return obj.discount_percentage() if obj.discount_percentage() else 0



class CreateProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class CartSerializer(serializers.ModelSerializer):
    product = ProductSerializer()  
    total_quantity = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = "__all__"
    
    def get_total_quantity(self, cart):
        return Cart.objects.filter(user=cart.user).aggregate(total_quantity=Sum('quantity'))['total_quantity']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        quantity = instance.quantity
        discounted_price = instance.product.discounted_price
        subtotal = quantity * discounted_price
        representation['subtotal'] = subtotal
        return representation

from .models import OrderItem
class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer()

    class Meta:
        model = OrderItem
        fields = ['product', 'quantity']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(source='orderitem_set', many=True)  
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Order
        fields = ['id', 'user', 'status', 'total_price', 'shipping_address', 'order_date', 'items']
