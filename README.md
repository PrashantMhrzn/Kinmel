# Kinmel

## Project Overview

Kinmel is an e-commerce API built with Django REST Framework. It provides a scalable backend solution for managing products, categories, sellers, customers, carts, orders, deliveries, and notifications. The system supports role-based authentication (Admin, Seller, Customer, Delivery) and enforces permissions to ensure secure data handling.  

With integrated features like order tracking, inventory management, and email notifications, Kinmel serves as a robust foundation for any online marketplace platform.  

---

## Features

- **Authentication & Permissions**
  - Token-based authentication
  - Role-based access control (Admin, Seller, Customer, Delivery)

- **Seller Features**
  - Seller Profile management
  - Seller Inventory with product management

- **Customer Features**
  - Cart system (add, update, remove items)
  - Checkout process → converts Cart into Order
  - Order tracking

- **Admin Features**
  - Category management
  - Full control of Orders and Deliveries
  - Analytics dashboard (revenue, orders, suppliers)

- **Delivery Features**
  - View assigned deliveries
  - Update delivery status

- **General Features**
  - CRUD operations with proper permissions
  - Filtering, searching, and ordering
  - Pagination (10 per page)
  - Notifications system per user
  - API responses formatted for RESTful consumption
  - Comprehensive Django Admin panel


---

## Setup Instructions

### Prerequisites
- Python **3.12+**
- PostgreSQL or SQLite for testing
- `pip`

### Installation

```bash
# Clone the repo
git clone https://github.com/prashantmhrzn/kinmel.git

# Go into the cloned directory
cd kinmel

# Setup virtual environment
python -m venv venv
# Activate it
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows

# Install dependencies
pip install -r requirements.txt

# Run database migrations
python manage.py migrate

# Create a superuser for admin panel
python manage.py createsuperuser

# Start the development server
python manage.py runserver
