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
# search_fields = ('title',)
# list_display = ('id', 'title')
# list_filter = ('name',)
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

admin.site.register(User, UserAdmin)

class SellerProfileAdmin(admin.ModelAdmin):
    search_fields = ('user__username', 'company_name', 'verified')
    list_display = ('user', 'company_name', 'verified')
    list_filter = ('user__username', 'verified')

admin.site.register(SellerProfile, SellerProfileAdmin)



