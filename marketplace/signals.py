from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Transaction, Item, Message
#交易功能的实现，还有一些bug
@receiver(post_save, sender=Transaction)
def handle_transaction_status_change(sender, instance, created, **kwargs):
    """处理交易状态变更的信号"""
    if created:
        # 新建交易时，将商品状态更新为已预订
        instance.item.status = 'reserved'
        instance.item.save()
        
        # 发送消息给卖家
        Message.objects.create(
            sender=instance.buyer,
            receiver=instance.seller,
            content=f"用户 {instance.buyer.username} 想要购买您的商品 '{instance.item.title}'。"
        )
    else:
        # 交易状态变更
        if instance.status == 'completed':
            # 交易完成，商品状态更新为已售出
            instance.item.status = 'sold'
            instance.item.save()
            
            # 发送消息给买家
            Message.objects.create(
                sender=instance.seller,
                receiver=instance.buyer,
                content=f"卖家已确认完成 '{instance.item.title}' 的交易。"
            )
        
        elif instance.status == 'rejected':
            # 交易被拒绝，商品状态恢复为可用
            instance.item.status = 'available'
            instance.item.save()
            
            # 发送消息给买家
            Message.objects.create(
                sender=instance.seller,
                receiver=instance.buyer,
                content=f"卖家已拒绝您购买 '{instance.item.title}' 的请求。"
            )
        
        elif instance.status == 'accepted':
            # 交易被接受
            # 发送消息给买家
            Message.objects.create(
                sender=instance.seller,
                receiver=instance.buyer,
                content=f"卖家已接受您购买 '{instance.item.title}' 的请求。"
            )
        
        elif instance.status == 'cancelled':
            # 交易被取消，商品状态恢复为可用
            instance.item.status = 'available'
            instance.item.save()
            
            # 发送消息给对方
            if instance.cancelled_by == instance.buyer:
                Message.objects.create(
                    sender=instance.buyer,
                    receiver=instance.seller,
                    content=f"买家已取消购买 '{instance.item.title}' 的请求。"
                )
            else:
                Message.objects.create(
                    sender=instance.seller,
                    receiver=instance.buyer,
                    content=f"卖家已取消 '{instance.item.title}' 的交易。"
                )

@receiver(pre_save, sender=Item)
def handle_item_status_change(sender, instance, **kwargs):
    """处理商品状态变更的信号"""
    # 检查是否是已存在的商品
    if instance.pk:
        try:
            old_instance = Item.objects.get(pk=instance.pk)
            # 如果商品状态从可用变为已删除，取消所有待处理的交易
            if old_instance.status == 'available' and instance.status == 'deleted':
                for transaction in Transaction.objects.filter(item=instance, status__in=['pending', 'accepted']):
                    transaction.status = 'cancelled'
                    transaction.save()
        except Item.DoesNotExist:
            pass
