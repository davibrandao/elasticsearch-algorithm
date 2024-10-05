from django.urls import path
from . import views

urlpatterns = [
    path('search/', views.search_items, name='search_items'),
    path('recommendations/<int:item_id>/', views.RecommendationView.as_view(), name='item-recommendations'),
    path('item/<int:item_id>/', views.item_detail, name='item_detail'),
]