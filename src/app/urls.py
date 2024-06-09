from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path('<str:pk>', views.detail_item, name="detail_item"),
    path('search/', views.search_view, name='search'),
]
