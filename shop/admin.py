from django.contrib import admin

from .models import Product, Cart, CartItem


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0


class CartAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'user', 'get_item_count', 'get_total', 'created_at']
    inlines = [CartItemInline]


admin.site.register(Product)
admin.site.register(Cart, CartAdmin)
admin.site.register(CartItem)
