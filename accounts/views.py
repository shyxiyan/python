from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.models import User
from .forms import UserRegisterForm, UserProfileForm, UserLoginForm, ReviewForm
from .models import UserProfile, Review
from marketplace.models import Transaction

def register(request):
    """用户注册视图"""
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()

            UserProfile.objects.get_or_create(user=user)
            login(request, user)
            messages.success(request, '注册成功！')
            return redirect('marketplace:home')
    else:
        form = UserRegisterForm()
    return render(request, 'accounts/register.html', {'form': form})


@login_required
def profile(request):
    """用户个人资料视图"""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
            messages.success(request, '个人资料已更新！')
            return redirect('accounts:profile')
    else:
        form = UserProfileForm(instance=request.user.profile)
    
    # 交易记录
    sold_transactions = Transaction.objects.filter(seller=request.user)
    bought_transactions = Transaction.objects.filter(buyer=request.user)
    
    # 评价
    reviews = Review.objects.filter(reviewee=request.user)
    
    context = {
        'form': form,
        'sold_transactions': sold_transactions,
        'bought_transactions': bought_transactions,
        'reviews': reviews,
    }
    return render(request, 'accounts/profile.html', context)

def user_detail(request, username):
    """查看其他用户资料视图"""
    user = get_object_or_404(User, username=username)
    reviews = Review.objects.filter(reviewee=user)
    
    context = {
        'profile_user': user,
        'reviews': reviews,
    }
    return render(request, 'accounts/user_detail.html', context)

@login_required
def add_review(request, transaction_id):
    """添加评价视图"""
    transaction = get_object_or_404(Transaction, id=transaction_id)
    
    # 检查是否有权限评价
    if request.user != transaction.buyer and request.user != transaction.seller:
        messages.error(request, '您没有权限评价此交易')
        return redirect('accounts:profile')
    
    # 确定评价对象
    if request.user == transaction.buyer:
        reviewee = transaction.seller
    else:
        reviewee = transaction.buyer
    
    # 检查是否已经评价过
    if Review.objects.filter(transaction=transaction, reviewer=request.user).exists():
        messages.error(request, '您已经评价过此交易')
        return redirect('accounts:profile')
    
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.transaction = transaction
            review.reviewer = request.user
            review.reviewee = reviewee
            review.save()
            messages.success(request, '评价已提交！')
            return redirect('accounts:profile')
    else:
        form = ReviewForm()
    
    context = {
        'form': form,
        'transaction': transaction,
        'reviewee': reviewee,
    }
    return render(request, 'accounts/add_review.html', context)
