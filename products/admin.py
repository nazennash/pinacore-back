from django.contrib import admin
from .models import MainCategory, SubCategory, SubTypeCategory, Product, Cart, Order

from django.contrib import admin
from .models import Product

class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'seller', 'price', 'discounted_price', 'created_at']
    search_fields = ['name', 'seller__username', 'seller__email']
    list_filter = ['seller', 'created_at']

admin.site.register(Product, ProductAdmin)
admin.site.register(MainCategory)
admin.site.register(SubCategory)
admin.site.register(SubTypeCategory)
admin.site.register(Cart)
admin.site.register(Order)
