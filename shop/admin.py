from django.contrib import admin

from .models import Product, Cart, CartItem, Order, OrderItem


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0


class CartAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'user', 'get_item_count', 'get_total', 'created_at']
    inlines = [CartItemInline]


admin.site.register(Product)
admin.site.register(Cart, CartAdmin)
admin.site.register(CartItem)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product', 'product_name', 'quantity', 'unit_price', 'subtotal', 'created_at']
    can_delete = False


class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'cellphone', 'total_amount', 'created_at']
    readonly_fields = ['cart', 'name', 'cellphone', 'address', 'total_amount', 'created_at']
    inlines = [OrderItemInline]


admin.site.register(Order, OrderAdmin)
