from django.shortcuts import render
from django.test import Client
from http import HTTPStatus

def home(request):
    # Initialize context first to avoid "local variable" error
    context = {
        'categories': [],
        'most_searched': [],
    }
    
    try:
        # Create Django test client
        client = Client()
        
        # Get categories
        categories_response = client.get('/api/v1/category/')
        
        if categories_response.status_code == 200:
            categories_data = categories_response.json()
            context['categories'] = categories_data.get('results', [])
            print("CATEGORIES:", len(context['categories']))
        else:
            print(f"Categories API Error: {categories_response.status_code}")

        # Get most searched products
        products_response = client.get('/api/v1/products/')
        if products_response.status_code == 200:
            products_data = products_response.json()
            products = products_data.get('results', [])
            # Take first 8 as most searched (you can add proper sorting later)
            context['most_searched'] = products[:8]
            print("MOST SEARCHED:", len(context['most_searched']))
        else:
            print(f"Products API Error: {products_response.status_code}")

        return render(request, 'index.html', context)
    
    except Exception as e:
        print(f"Exception: {e}")
        # Context is already defined, so no error here
        return render(request, 'index.html', context)

def login(request):
    return render(request, 'login.html')

def register(request):
    return render(request, 'register.html')