from django import forms
from django.utils import timezone
from .models import BidItem, Bid, BidItemImage
from foundapp.models import Item

class BidItemForm(forms.ModelForm):
    class Meta:
        model = BidItem
        fields = ['title', 'description', 'initial_price', 'min_increment', 'image', 'end_date', 'related_item']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control bg-navy-blue-light text-white',
                'placeholder': 'Enter a descriptive title',
                'required': True
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control bg-navy-blue-light text-white',
                'rows': 4,
                'placeholder': 'Provide details about your item',
                'required': True
            }),
            'initial_price': forms.NumberInput(attrs={
                'class': 'form-control bg-navy-blue-light text-white',
                'min': '0.01',
                'step': '0.01',
                'placeholder': 'Starting bid price',
                'required': True
            }),
            'min_increment': forms.NumberInput(attrs={
                'class': 'form-control bg-navy-blue-light text-white',
                'min': '0.01',
                'step': '0.01',
                'placeholder': 'Minimum bid increment',
                'required': True
            }),
            'end_date': forms.DateTimeInput(attrs={
                'class': 'form-control bg-navy-blue-light text-white',
                'type': 'datetime-local',
                'required': True
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control bg-navy-blue-light text-white',
                'required': True
            }),
            'related_item': forms.Select(attrs={
                'class': 'form-control bg-navy-blue-light text-white'
            })
        }
        
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            self.fields['related_item'].queryset = Item.objects.filter(user=user)
        
        self.fields['min_increment'].initial = 1.00

    def clean_end_date(self):
        end_date = self.cleaned_data.get('end_date')
        if end_date and end_date <= timezone.now():
            raise forms.ValidationError("End date must be in the future.")
        return end_date

    def clean_initial_price(self):
        initial_price = self.cleaned_data.get('initial_price')
        if initial_price and initial_price <= 0:
            raise forms.ValidationError("Initial price must be greater than zero.")
        return initial_price

class BidItemImageForm(forms.ModelForm):
    image = forms.ImageField(
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control bg-navy-blue-light text-white',
            'accept': 'image/*'
        })
    )

    class Meta:
        model = BidItemImage
        fields = ['image']

class PlaceBidForm(forms.ModelForm):
    class Meta:
        model = Bid
        fields = ['amount']
        widgets = {
            'amount': forms.NumberInput(attrs={
                'class': 'form-control bg-navy-blue-light text-white',
                'min': '0.01',
                'step': '0.01'
            })
        }
    
    def __init__(self, *args, **kwargs):
        self.bid_item = kwargs.pop('bid_item', None)
        super().__init__(*args, **kwargs)
        
        if self.bid_item:
            min_bid = self.bid_item.current_price + self.bid_item.min_increment
            self.fields['amount'].widget.attrs.update({
                'min': min_bid,
                'value': min_bid
            })
            self.fields['amount'].help_text = f'Minimum bid: ${min_bid}'
    
    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if self.bid_item:
            min_bid = self.bid_item.current_price + self.bid_item.min_increment
            if amount < min_bid:
                raise forms.ValidationError(f'Your bid must be at least ${min_bid}')
        return amount