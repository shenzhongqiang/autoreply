from django.urls import path
from . import views

urlpatterns = [
    path('keyword/', views.keyword, name='keyword'),
]
