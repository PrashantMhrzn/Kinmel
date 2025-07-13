from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as UA
from .models import *
from .forms import CustomUserCreationForm, CustomUserChangeForm
# Register your models here.
# Text changes in admin page
admin.site.site_header = "Kinmel Admin"
admin.site.site_title = "Kinmel"
admin.site.index_title = "Welcome to Kinmel Admin Page"
# since we have created a custom user, we have to register it using the UserAdmin class to have
# all the default values for Abstract User
class UserAdmin(UA):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User
    list_display = ('username', 'email', 'role', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_active')
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Personal Info', {'fields': ('role', 'phone', 'address')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'role', 'phone', 'address', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )
    search_fields = ('email', 'username')
    ordering = ('username',)
    list_per_page = 15


admin.site.register(User, UserAdmin)

class SellerInventoryInline(admin.TabularInline):
    model = SellerInventory
    extra = 3
    max_num = 50

class SellerProfileAdmin(admin.ModelAdmin):
    search_fields = ('user__username', 'company_name', 'verified')
    list_display = ('user', 'company_name', 'verified')
    list_filter = ('user__username', 'verified')
    list_per_page = 15
    list_editable = ('verified',)
    inlines = [SellerInventoryInline]


admin.site.register(SellerProfile, SellerProfileAdmin)

class CategoryAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    list_display = ('name',)
    list_filter = ('name',)
    list_per_page = 15

admin.site.register(Category, CategoryAdmin)

class ProductAdmin(admin.ModelAdmin):
    search_fields = ('name', 'price', 'seller__username')
    list_display = ('name','price', 'seller__username')
    list_filter = ('name','price', 'seller__username')
    list_per_page = 15

admin.site.register(Product, ProductAdmin)


class SellerInventoryAdmin(admin.ModelAdmin):
    search_fields = ('seller__username', 'product__name')
    list_display = ('seller__username', 'product__name', 'stock_quantity')
    list_filter = ('seller__username', 'product__name')
    list_per_page = 15

admin.site.register(SellerInventory, SellerInventoryAdmin)

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 1 # blank forms to show

class CartAdmin(admin.ModelAdmin):
    search_fields = ('user__username', 'user__phone')
    list_display = ('user', 'user__phone', 'total_price')
    list_filter = ('user__username',)
    list_per_page = 15
    inlines = [CartItemInline]

admin.site.register(Cart, CartAdmin)

class CartItemAdmin(admin.ModelAdmin):
    search_fields = ('cart__user__username', 'product__name')
    list_display = ('cart', 'product__name')
    list_filter = ('cart__user__username', 'product__name')
    list_per_page = 15

admin.site.register(CartItem, CartItemAdmin)

# Inline class for order
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1 # blank forms to show

class OrderAdmin(admin.ModelAdmin):
    search_fields = ('customer__username', 'status')
    list_display = ('customer__username', 'status')
    list_filter = ('customer__username', 'status')
    list_per_page = 15
    inlines = [OrderItemInline]

admin.site.register(Order, OrderAdmin)

class OrderItemAdmin(admin.ModelAdmin):
    search_fields = ('order', 'product__name')
    list_display = ('order__customer__username', 'product__name')
    list_filter = ('order__customer__username', 'product__name')
    list_per_page = 15

admin.site.register(OrderItem, OrderItemAdmin)

class DeliveryAdmin(admin.ModelAdmin):
    search_fields = ('order__customer__username', 'delivery_person', 'status')
    list_display = ('order__customer__username', 'delivery_person', 'status')
    list_filter = ('order__customer__username', 'delivery_person', 'status')
    list_per_page = 15

admin.site.register(Delivery, DeliveryAdmin)

class NotificationAdmin(admin.ModelAdmin):
    search_fields = ('user__username', 'seen', 'created_at')
    list_display = ('user__username', 'seen', 'created_at')
    list_filter = ('user__username', 'seen', 'created_at')
    list_per_page = 15

admin.site.register(Notification, NotificationAdmin)
