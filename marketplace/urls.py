from django.urls import path
from . import views

app_name = 'marketplace'
#有关商品的总路由
urlpatterns = [
    path('', views.home, name='home'),
    path('items/', views.item_list, name='item_list'),
    path('items/<int:item_id>/', views.item_detail, name='item_detail'),
    path('items/create/', views.item_create, name='item_create'),
    path('items/<int:item_id>/update/', views.item_update, name='item_update'),
    path('items/<int:item_id>/delete/', views.item_delete, name='item_delete'),
    path('items/<int:item_id>/favorite/', views.toggle_favorite, name='toggle_favorite'),
    path('my-items/', views.my_items, name='my_items'),
    path('my-favorites/', views.my_favorites, name='my_favorites'),
    path('items/<int:item_id>/buy/', views.create_transaction, name='create_transaction'),
    path('my-transactions/', views.my_transactions, name='my_transactions'),
    path('transactions/<int:transaction_id>/', views.transaction_detail, name='transaction_detail'),
    path('transactions/<int:transaction_id>/update/', views.transaction_update, name='transaction_update'),
    path('my-messages/', views.my_messages, name='my_messages'),
    path('send-message/<int:user_id>/', views.send_message, name='send_message'),
]
