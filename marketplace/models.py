from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
"""此处为所有的商品模型"""
class Category(models.Model):
    """商品分类模型"""
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = _('商品分类')
        verbose_name_plural = _('商品分类')

    def __str__(self):
        return self.name


class Item(models.Model):
    """商品模型"""
    STATUS_CHOICES = (
        ('available', '可用'),
        ('sold', '已售出'),
        ('reserved', '已预订'),
        ('deleted', '已删除'),
    )
    
    CONDITION_CHOICES = (
        ('new', '全新'),
        ('like_new', '几乎全新'),
        ('good', '良好'),
        ('fair', '一般'),
        ('poor', '较差'),
    )
    
    title = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='items')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='items')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('商品')
        verbose_name_plural = _('商品')
        ordering = ['-created_at']
        
    def __str__(self):
        return self.title
    
    @property
    def is_available(self):
        return self.status == 'available'


class ItemImage(models.Model):
    """商品图片模型"""
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='items/')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('商品图片')
        verbose_name_plural = _('商品图片')
        
    def __str__(self):
        return f"{self.item.title}的图片"


class Favorite(models.Model):
    """收藏模型"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='favorites')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('收藏')
        verbose_name_plural = _('收藏')
        unique_together = ('user', 'item')
        
    def __str__(self):
        return f"{self.user.username}收藏的{self.item.title}"


class Transaction(models.Model):
    """交易模型"""
    STATUS_CHOICES = (
        ('pending', '等待确认'),
        ('accepted', '已接受'),
        ('rejected', '已拒绝'),
        ('completed', '已完成'),
        ('cancelled', '已取消'),
    )
    
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='transactions')
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sold_transactions')
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bought_transactions')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('交易')
        verbose_name_plural = _('交易')
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.buyer.username}购买{self.item.title}"
    
    def save(self, *args, **kwargs):
        """当交易完成时自动更新商品状态"""
        if self.status == 'completed' and self.pk is None:  # 新创建的交易
            self.item.status = 'sold'
            self.item.save()
        super().save(*args, **kwargs)


class Message(models.Model):
    """消息模型"""
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('消息')
        verbose_name_plural = _('消息')
        ordering = ['-created_at']
        
    def __str__(self):
        return f"从{self.sender.username}到{self.receiver.username}的消息"
