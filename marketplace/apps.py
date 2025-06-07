from django.apps import AppConfig


class MarketplaceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'marketplace'
    
    def ready(self):
        # 导入信号处理器
        import marketplace.signals
