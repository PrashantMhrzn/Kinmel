from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User, Product

# To display while creating Users in Admin, the fields are displayed additionally to the default values
# For adding users
class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'role', 'phone', 'address')

# For updating users
class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'role', 'phone', 'address')

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'image']

