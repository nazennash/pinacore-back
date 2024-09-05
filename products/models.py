from django.db import models
from users.models import CustomUser as User

# Choices for product size
SIZES = (
    ("Xtra Large", "Xtra Large"),
    ("Large", "Large"),
    ("Medium", "Medium"),
    ("Small", "Small")
)


# Main Category Model
class MainCategory(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    image = models.ImageField(upload_to='media/main_categories', null=True, blank=True)

    def __str__(self):
        return self.name


# Sub Category Model
class SubCategory(models.Model):
    main_category = models.ForeignKey(MainCategory, on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    image = models.ImageField(upload_to='media/sub_categories', null=True, blank=True)

    def __str__(self):
        return self.name


# Sub Type Category Model
class SubTypeCategory(models.Model):
    sub_category = models.ForeignKey(SubCategory, on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.name


# Product Image Model for storing multiple images
class ProductImage(models.Model):
    image = models.ImageField(upload_to='media/product_images/')
    alt_text = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.alt_text or "Image"


# Product Model
class Product(models.Model):
    main_category = models.ForeignKey(MainCategory, on_delete=models.CASCADE, null=True, blank=True)
    sub_category = models.ForeignKey(SubCategory, on_delete=models.CASCADE, null=True, blank=True)
    sub_type_category = models.ForeignKey(SubTypeCategory, on_delete=models.CASCADE, null=True, blank=True)
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='products', null=True, blank=True)
    
    name = models.CharField(max_length=50, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    discounted_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    images = models.ManyToManyField(ProductImage)  # Allowing multiple images
    brand = models.CharField(max_length=255, null=True, blank=True)
    size = models.CharField(max_length=50, choices=SIZES, blank=True, null=True)
    color = models.CharField(max_length=50, null=True, blank=True)
    quantity = models.PositiveIntegerField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def discount_percentage(self):
        if self.discounted_price:
            return int(((self.price - self.discounted_price) / self.price) * 100)
        return 0


# Cart Model
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
    quantity = models.PositiveIntegerField(default=1)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def total_cost(self):
        return self.quantity * (self.product.discounted_price or self.product.price)

    def __str__(self):
        return str(self.product)


# Order Model
class Order(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Processing', 'Processing'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    products = models.ManyToManyField(Product, through='OrderItem')  # Using OrderItem to track products
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


# Order Item Model to track quantity for each product in the order
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def save(self, *args, **kwargs):
        # Reduce product quantity after saving order item
        self.product.quantity -= self.quantity
        self.product.save()
        super().save(*args, **kwargs)
