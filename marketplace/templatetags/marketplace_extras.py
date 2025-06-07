from django import template
from django.db.models import Count

register = template.Library()

@register.filter
def get_item_image_count(item):
    """返回商品的图片数量"""
    return item.images.count()

@register.filter
def get_unread_message_count(user):
    """返回用户未读消息数量"""
    return user.received_messages.filter(is_read=False).count()

@register.simple_tag
def get_popular_categories(limit=5):
    """获取最受欢迎的商品分类"""
    from marketplace.models import Category, Item
    return Category.objects.annotate(
        item_count=Count('items')
    ).filter(item_count__gt=0).order_by('-item_count')[:limit]
