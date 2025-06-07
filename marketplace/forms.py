from django import forms
from .models import Item, ItemImage, Transaction, Message, Category

class ItemForm(forms.ModelForm):
    """商品发布表单"""
    class Meta:
        model = Item
        fields = ['title', 'description', 'price', 'condition', 'category']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
        }

class ItemImageForm(forms.Form):
    """商品图片上传表单"""
    images = forms.ImageField(
        label='商品图片',
        widget=forms.ClearableFileInput(),
        required=False
    )

class ItemSearchForm(forms.Form):
    """商品搜索表单"""
    query = forms.CharField(required=False, label='关键词')
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        empty_label="所有分类",
        label='分类'
    )
    min_price = forms.DecimalField(required=False, min_value=0, label='最低价格')
    max_price = forms.DecimalField(required=False, min_value=0, label='最高价格')
    condition = forms.ChoiceField(
        choices=[('', '所有状态')] + list(Item.CONDITION_CHOICES),
        required=False,
        label='商品状态'
    )

class TransactionForm(forms.ModelForm):
    """交易表单"""
    message = forms.CharField(
        label='给卖家的留言',
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False
    )
    
    class Meta:
        model = Transaction
        fields = ['message']

class MessageForm(forms.ModelForm):
    """消息表单"""
    class Meta:
        model = Message
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3}),
        }
