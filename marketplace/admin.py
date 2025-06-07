from django.contrib import admin
from .models import Category, Item, ItemImage, Transaction, Message, Favorite

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

class ItemImageInline(admin.TabularInline):
    model = ItemImage
    extra = 1

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'price', 'user', 'category', 'condition', 'status', 'created_at')
    list_filter = ('status', 'condition', 'category', 'created_at')
    search_fields = ('title', 'description', 'user__username')
    inlines = [ItemImageInline]

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('item', 'seller', 'buyer', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('item__title', 'seller__username', 'buyer__username')

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('sender__username', 'receiver__username', 'content')

@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'item', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'item__title')
