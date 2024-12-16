from django.contrib import admin
from .models import Book, CartItem,UserProfile

admin.site.register(Book)
admin.site.register(CartItem)
admin.site.register(UserProfile)



