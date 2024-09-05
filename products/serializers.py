from rest_framework import serializers
from .models import MainCategory, SubCategory, SubTypeCategory, Product, Cart, Order

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


class ProductSerializer(serializers.ModelSerializer):
    seller = serializers.ReadOnlyField(source='seller.username')
    main_category = serializers.PrimaryKeyRelatedField(queryset=MainCategory.objects.all())
    sub_category = serializers.PrimaryKeyRelatedField(queryset=SubCategory.objects.all())
    sub_type_category = serializers.PrimaryKeyRelatedField(queryset=SubTypeCategory.objects.all())
    discount_percentage = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Product
        fields = '__all__'

    def get_discount_percentage(self, obj):
        return obj.discount_percentage()


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

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'