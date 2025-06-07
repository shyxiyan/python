from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from django.db.models import Q

class EmailBackend(ModelBackend):
    """自定义认证后端，支持邮箱登录"""
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # 检查是否是邮箱登录
            if '@' in username:
                user = User.objects.get(email=username)
            else:
                user = User.objects.get(username=username)
                
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None
        
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
