from django.contrib import admin
from .models import UserProfile, Review

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'created_at', 'updated_at')
    search_fields = ('user__username', 'user__email', 'phone')
    list_filter = ('created_at', 'updated_at')

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('reviewer', 'reviewee', 'rating', 'created_at')
    search_fields = ('reviewer__username', 'reviewee__username', 'comment')
    list_filter = ('rating', 'created_at')
