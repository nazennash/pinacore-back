from django.contrib import admin
from .models import MainCategory, SubCategory, SubTypeCategory, Product, Cart, Order

# Register your models here.

admin.site.register(MainCategory)
admin.site.register(SubCategory)
admin.site.register(SubTypeCategory)
admin.site.register(Product)
admin.site.register(Cart)
admin.site.register(Order)
