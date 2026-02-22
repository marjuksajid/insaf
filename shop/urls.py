from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('cart/', views.cart, name='cart'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('update-cart/<int:item_id>/', views.update_cart, name='update_cart'),
    path('remove-from-cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('register/', views.register, name='register'),
    path('<slug:link>/', views.product_detail, name='product_detail'),
    # The `name` parameter in the `path` function is used to give a name
    # to the URL pattern. This name can be used to refer to the URL pattern in other parts of your code
    # the `product_detail` view function expects a parameter called `link`, which is captured 
    # from the URL pattern. The `<slug:link>/` part of the URL pattern captures a slug from
    # the URL and passes it as an argument to the `product_detail` view function.
    # So when a user visits a URL that matches this pattern, the corresponding product's
    # slug will be passed to the view function
]