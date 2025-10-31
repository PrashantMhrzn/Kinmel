from django.shortcuts import render
from api.models import Product, Category
import requests
from http import HTTPStatus
# Create your views here.
def home(request):
    try:
        # fetch data from api
        api_base_url = "http://localhost:8000/api/v1"

        categories_response = requests.get(f'{api_base_url}/category/')

        if categories_response.status_code == 200:
            categories = categories_response.json()
            print(categories)
        else:
            categories = []

        context = {
            # 'featured_products': featured_products,
            'categories': categories,
        }

        return render(request, 'index.html', context)
    except:
        pass

def login(request):
    return render(request, 'login.html')

def register(request):
    return render(request, 'register.html')

