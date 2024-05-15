# myapp/urls.py

from . import views
from django.urls import path
from .views import upload_image

urlpatterns = [
    path('', views.home, name='home'),  # Define URL pattern for the home view
    # Add more URL patterns as needed
]





urlpatterns = [
    path('upload/', views.upload_image, name='upload_image'),
]
