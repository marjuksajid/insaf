from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User
from unidecode import unidecode

class Product(models.Model):
    name = models.CharField(max_length=100)
    amount = models.CharField(max_length=50)
    description = models.TextField(max_length=500)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    image = models.ImageField(upload_to='shop/products/')
    link = models.SlugField(max_length=100, unique=True, blank=True, editable=False)
    # The SlugField is used to store a URL-friendly version of the product's name or ID.
    # The field is not seeking any text to be entered by the admin
    # The `slugify` function in Django handles Unicode characters properly
    # For example "আজোয়া খেজুর" will be slugified to "আজোয়া-খেজুর"
    def save(self, *args, **kwargs):
        if not self.link:
            self.link = slugify(unidecode(self.name + "-" + self.amount))
            # The `unidecode` function is used to convert the Bengali characters in the product name to their closest ASCII representation before slugifying it. This ensures that the generated slug is URL-friendly and can be used in your product URLs without any issues, even if the product name contains non-Latin characters.
            # The `amount` is added to the slug to ensure uniqueness in case there are multiple products with the same name.
        super().save(*args, **kwargs)
    def __str__(self):
        return self.name


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart ({self.session_key})"

    def get_total(self):
        return sum(item.get_subtotal() for item in self.items.all())

    def get_item_count(self):
        return sum(item.quantity for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('cart', 'product')

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    def get_subtotal(self):
        return self.product.price * self.quantity

class Order(models.Model):
    cart = models.OneToOneField(Cart, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    cellphone = models.CharField(max_length=20)
    address = models.TextField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} - {self.name}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    product_name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.quantity} x {self.product_name} (Order #{self.order_id})"
