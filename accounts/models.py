from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
"""此处存放与用户有关的模型"""
class UserProfile(models.Model):
    """用户个人资料模型，扩展Django内置的User模型"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    """一个class就相当于在数据库中创建了一个表"""

    class Meta:
        verbose_name = _('用户资料')
        verbose_name_plural = _('用户资料')

    def __str__(self):
        return f"{self.user.username}的个人资料"

    @property
    def rating(self):
        """获取用户的平均评分"""
        reviews = Review.objects.filter(reviewee=self.user)
        if reviews.exists():
            return reviews.aggregate(models.Avg('rating'))['rating__avg']
        return 0


class Review(models.Model):
    """用户评价模型"""
    transaction = models.ForeignKey('marketplace.Transaction', on_delete=models.CASCADE, related_name='reviews')
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews_given')
    reviewee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews_received')
    rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('用户评价')
        verbose_name_plural = _('用户评价')
        unique_together = ('transaction', 'reviewer')

    def __str__(self):
        return f"{self.reviewer.username}对{self.reviewee.username}的评价"
