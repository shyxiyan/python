from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.contrib.auth.models import User
from .models import Item, ItemImage, Transaction, Message, Category, Favorite
from .forms import ItemForm, ItemImageForm, ItemSearchForm, TransactionForm, MessageForm

def home(request):
    """首页视图"""
    # 获取最新发布的商品
    latest_items = Item.objects.filter(status='available').order_by('-created_at')[:8]
    # 获取所有分类
    categories = Category.objects.all()
    
    context = {
        'latest_items': latest_items,
        'categories': categories,
    }
    return render(request, 'marketplace/home.html', context)

def item_list(request):
    """商品列表视图"""
    form = ItemSearchForm(request.GET)
    items = Item.objects.filter(status='available')
    
    # 搜索过滤
    if form.is_valid():
        query = form.cleaned_data.get('query')
        category = form.cleaned_data.get('category')
        min_price = form.cleaned_data.get('min_price')
        max_price = form.cleaned_data.get('max_price')
        condition = form.cleaned_data.get('condition')
        
        if query:
            items = items.filter(Q(title__icontains=query) | Q(description__icontains=query))
        if category:
            items = items.filter(category=category)
        if min_price:
            items = items.filter(price__gte=min_price)
        if max_price:
            items = items.filter(price__lte=max_price)
        if condition:
            items = items.filter(condition=condition)
    
    # 分页
    paginator = Paginator(items, 12)  # 每页12个商品
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'form': form,
        'page_obj': page_obj,
    }
    return render(request, 'marketplace/item_list.html', context)

def item_detail(request, item_id):
    """商品详情视图"""
    item = get_object_or_404(Item, id=item_id)
    is_favorite = False
    
    if request.user.is_authenticated:
        is_favorite = Favorite.objects.filter(user=request.user, item=item).exists()
    
    # 相关商品推荐
    related_items = Item.objects.filter(
        category=item.category, 
        status='available'
    ).exclude(id=item.id)[:4]
    
    context = {
        'item': item,
        'is_favorite': is_favorite,
        'related_items': related_items,
    }
    return render(request, 'marketplace/item_detail.html', context)

@login_required
def item_create(request):
    """创建商品视图"""
    if request.method == 'POST':
        form = ItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.user = request.user
            item.save()
            
            # 处理图片上传
            if 'images' in request.FILES:
                image = request.FILES['images']
                ItemImage.objects.create(item=item, image=image)
            
            messages.success(request, '商品发布成功！')
            return redirect('marketplace:item_detail', item_id=item.id)
    else:
        form = ItemForm()
    
    context = {
        'form': form,
        'image_form': ItemImageForm(),
    }
    return render(request, 'marketplace/item_form.html', context)

@login_required
def item_update(request, item_id):
    """更新商品视图"""
    item = get_object_or_404(Item, id=item_id)
    
    # 检查权限
    if request.user != item.user:
        messages.error(request, '您没有权限编辑此商品')
        return redirect('marketplace:item_detail', item_id=item.id)
    
    if request.method == 'POST':
        form = ItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            
            # 处理图片上传
            if 'images' in request.FILES:
                image = request.FILES['images']
                ItemImage.objects.create(item=item, image=image)
            
            messages.success(request, '商品信息已更新！')
            return redirect('marketplace:item_detail', item_id=item.id)
    else:
        form = ItemForm(instance=item)
    
    context = {
        'form': form,
        'image_form': ItemImageForm(),
        'item': item,
    }
    return render(request, 'marketplace/item_form.html', context)

@login_required
def item_delete(request, item_id):
    """删除商品视图"""
    item = get_object_or_404(Item, id=item_id)
    
    # 检查权限
    if request.user != item.user:
        messages.error(request, '您没有权限删除此商品')
        return redirect('marketplace:item_detail', item_id=item.id)
    
    if request.method == 'POST':
        item.status = 'deleted'
        item.save()
        messages.success(request, '商品已删除！')
        return redirect('marketplace:my_items')
    
    return render(request, 'marketplace/item_confirm_delete.html', {'item': item})

@login_required
def toggle_favorite(request, item_id):
    """切换收藏状态视图"""
    item = get_object_or_404(Item, id=item_id)
    
    favorite, created = Favorite.objects.get_or_create(user=request.user, item=item)
    
    if not created:
        favorite.delete()
        is_favorite = False
    else:
        is_favorite = True
    
    # 检查是否是AJAX请求
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'is_favorite': is_favorite})
    
    return redirect('marketplace:item_detail', item_id=item.id)

@login_required
def my_items(request):
    """我的商品视图"""
    items = Item.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'marketplace/my_items.html', {'items': items})

@login_required
def my_favorites(request):
    """我的收藏视图"""
    favorites = Favorite.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'marketplace/my_favorites.html', {'favorites': favorites})

@login_required
def create_transaction(request, item_id):
    """创建交易视图"""
    item = get_object_or_404(Item, id=item_id)
    
    # 检查商品是否可用
    if item.status != 'available':
        messages.error(request, '该商品已不可用')
        return redirect('marketplace:item_detail', item_id=item.id)
    
    # 检查是否是自己的商品
    if request.user == item.user:
        messages.error(request, '不能购买自己的商品')
        return redirect('marketplace:item_detail', item_id=item.id)
    
    # 检查是否已经有未完成的交易
    if Transaction.objects.filter(item=item, buyer=request.user, status__in=['pending', 'accepted']).exists():
        messages.error(request, '您已经有一个关于此商品的交易正在进行中')
        return redirect('marketplace:item_detail', item_id=item.id)
    
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.item = item
            transaction.seller = item.user
            transaction.buyer = request.user
            transaction.message = form.cleaned_data.get('message', '')
            transaction.save()
            
            messages.success(request, '交易请求已发送！')
            return redirect('marketplace:my_transactions')
    else:
        form = TransactionForm()
    
    context = {
        'form': form,
        'item': item,
    }
    return render(request, 'marketplace/transaction_form.html', context)

@login_required
def my_transactions(request):
    """我的交易视图"""
    # 作为买家的交易
    bought_transactions = Transaction.objects.filter(buyer=request.user).order_by('-created_at')
    # 作为卖家的交易
    sold_transactions = Transaction.objects.filter(seller=request.user).order_by('-created_at')
    
    context = {
        'bought_transactions': bought_transactions,
        'sold_transactions': sold_transactions,
    }
    return render(request, 'marketplace/my_transactions.html', context)

@login_required
def transaction_detail(request, transaction_id):
    """交易详情视图"""
    transaction = get_object_or_404(Transaction, id=transaction_id)
    
    # 检查权限
    if request.user != transaction.buyer and request.user != transaction.seller:
        messages.error(request, '您没有权限查看此交易')
        return redirect('marketplace:my_transactions')
    
    context = {
        'transaction': transaction,
    }
    return render(request, 'marketplace/transaction_detail.html', context)

@login_required
def transaction_update(request, transaction_id):
    """更新交易状态视图"""
    transaction = get_object_or_404(Transaction, id=transaction_id)
    
    # 检查权限
    if request.user != transaction.seller and request.user != transaction.buyer:
        messages.error(request, '您没有权限更新此交易')
        return redirect('marketplace:transaction_detail', transaction_id=transaction.id)
    
    if request.method == 'POST':
        status = request.POST.get('status')
        
        if status in ['accepted', 'rejected', 'completed', 'cancelled']:
            transaction.status = status
            
            # 根据状态更新商品状态
            if status == 'rejected' or status == 'cancelled':
                transaction.item.status = 'available'
                transaction.item.save()
                if request.user == transaction.buyer:
                    transaction.cancelled_by = transaction.buyer
                else:
                    transaction.cancelled_by = transaction.seller
            elif status == 'completed':
                transaction.item.status = 'sold'
                transaction.item.save()
            
            transaction.save()
            
            messages.success(request, '交易状态已更新！')
        else:
            messages.error(request, '无效的操作')
            
        return redirect('marketplace:transaction_detail', transaction_id=transaction.id)
    
    return render(request, 'marketplace/transaction_detail.html', {'transaction': transaction})

@login_required
def my_messages(request):
    """我的消息视图"""
    # 获取与当前用户有消息往来的所有用户
    contacts = User.objects.filter(
        Q(sent_messages__receiver=request.user) | 
        Q(received_messages__sender=request.user)
    ).distinct()
    
    # 为每个联系人添加未读消息计数
    for contact in contacts:
        contact.unread_count = Message.objects.filter(
            sender=contact, 
            receiver=request.user, 
            is_read=False
        ).count()
    
    # 如果是AJAX请求，返回与特定用户的消息
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        user_id = request.GET.get('user_id')
        if user_id:
            messages_list = Message.objects.filter(
                (Q(sender=request.user) & Q(receiver_id=user_id)) |
                (Q(receiver=request.user) & Q(sender_id=user_id))
            ).order_by('created_at')
            
            # 标记消息为已读
            unread_messages = messages_list.filter(receiver=request.user, is_read=False)
            unread_messages.update(is_read=True)
            
            # 准备JSON响应
            messages_data = []
            for msg in messages_list:
                messages_data.append({
                    'id': msg.id,
                    'content': msg.content,
                    'sender_id': msg.sender.id,
                    'receiver_id': msg.receiver.id,
                    'created_at': msg.created_at.strftime('%Y-%m-%d %H:%M'),
                    'is_read': msg.is_read
                })
            
            return JsonResponse({
                'messages': messages_data,
                'current_user_id': request.user.id
            })
    
    context = {
        'contacts': contacts,
    }
    return render(request, 'marketplace/my_messages.html', context)

@login_required
def send_message(request, user_id):
    """发送消息视图"""
    receiver = get_object_or_404(User, id=user_id)
    
    # 不能给自己发消息
    if receiver == request.user:
        messages.error(request, '不能给自己发消息')
        return redirect('marketplace:my_messages')
    
    if request.method == 'POST':
        content = request.POST.get('content')
        
        if content:
            message = Message.objects.create(
                sender=request.user,
                receiver=receiver,
                content=content
            )
            
            # 如果是AJAX请求，返回成功响应
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True})
            
            messages.success(request, '消息已发送！')
            return redirect('marketplace:my_messages')
    
    context = {
        'receiver': receiver,
        'form': MessageForm(),
    }
    return render(request, 'marketplace/send_message.html', context)
