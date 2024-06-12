from django.db import models
from users.models import CustomUser as User


SIZES = (
    ("Xtra Large", "Xtra Large"),
    ("Large", "Large"),
    ("Medium", "Medium"),
    ("Small", "Small")
)

class MainCategory(models.Model):
    name = models.CharField(max_length=255, blank=True)
    image = models.ImageField(upload_to='images')

    def __str__(self):
        return self.name

class SubCategory(models.Model):
    main_category = models.ForeignKey(MainCategory, on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length=255, blank=True)
    image = models.ImageField(upload_to='images')

    def __str__(self):
        return self.name

class SubTypeCategory(models.Model):
    sub_category = models.ForeignKey(SubCategory, on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length=255, blank=True)
    image = models.ImageField(upload_to='images')

    def __str__(self):
        return self.name

class Product(models.Model):
    main_category = models.ForeignKey(MainCategory, on_delete=models.CASCADE)
    sub_category = models.ForeignKey(SubCategory, on_delete=models.CASCADE)
    sub_type_category = models.ForeignKey(SubTypeCategory, on_delete=models.CASCADE)
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='products')


    name = models.CharField(max_length=50)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discounted_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    image = models.ImageField(upload_to='images/', null=True, blank=True)
    brand = models.CharField(max_length=255, null=True, blank=True)
    size = models.CharField(max_length=50, choices=SIZES, blank=True, null=True)
    color = models.CharField(max_length=50, null=True, blank=True)
    custom_attributes = models.JSONField(null=True, blank=True)


    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def discount_percentage(self):
        if self.discounted_price:
            return int(((self.price - self.discounted_price) / self.price) * 100)
        return 0

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
    quantity = models.PositiveIntegerField(default=1)
    session_key = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def total_cost(self):
        return self.quantity * (self.product.discounted_price or self.product.price)

    def __str__(self):
        return str(self.product)

class Order(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Processing', 'Processing'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    products = models.ManyToManyField(Product)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    shipping_address = models.TextField(null=True)
    order_date = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} -- {self.id}"

    class Meta:
        ordering = ['-updated', '-created']
