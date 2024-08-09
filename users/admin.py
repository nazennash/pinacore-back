from django.contrib import admin
from .models import CustomUser

# Register your models here.

# admin.site.register(CustomUser)


from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('display_name', 'username', 'phone_number', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active')
    fieldsets = (
        (None, {'fields': ('email', 'username', 'name', 'phone_number', 'otp', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_superuser', 'is_buyer', 'is_seller')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'phone_number', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )
    search_fields = ('email', 'username', 'phone_number')
    ordering = ('email',)

    def display_name(self, obj):
        if obj.is_seller:  
            return "seller"
        elif obj.is_buyer:  
            return "buyer"
        return None  

    display_name.admin_order_field = 'email'  # Optionally, specify the field to order by
    display_name.short_description = 'entry'  # Custom header for the column

admin.site.register(CustomUser, CustomUserAdmin)

