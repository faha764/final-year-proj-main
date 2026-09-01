
from django import forms
from .models import Category, Customer
from .models import Product


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']


class CustomerForm(forms.ModelForm):
    confirm_password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = Customer
        fields = ['name', 'email', 'contact', 'password']
        widgets = {
            'password': forms.PasswordInput(),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm = cleaned_data.get("confirm_password")

        if password != confirm:
            self.add_error('confirm_password', "Passwords do not match")


class CustomerLoginForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-input',
        'placeholder': 'Enter your email',
        'required': True
    }))
    
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-input',
        'placeholder': 'Enter your password',
        'required': True
    }))

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'price', 'quantity', 'description', 'category', 'customized', 'image']

from django import forms
from .models import Seller

class SellerProfileForm(forms.ModelForm):
    class Meta:
        model = Seller
        fields = ['full_name', 'username', 'dob', 'shop_name', 'experience', 'skills', 'city', 'profile_image', 'additional_details']

# forms.py
from django import forms
from .models import ShippingDetail

class ShippingDetailForm(forms.ModelForm):
    class Meta:
        model = ShippingDetail
        fields = ['full_name', 'address', 'city', 'phone', 'email']
        from django import forms

class PaymentForm(forms.Form):
    payment_screenshot = forms.ImageField()

class CustomerSignupForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'email', 'contact', 'password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm = cleaned_data.get("confirm_password")

        if password != confirm:
            self.add_error('confirm_password', "Passwords do not match")        
            from django import forms
from .models import Seller
class SellerLoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)


class CustomerForm(forms.ModelForm):
    confirm_password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = Customer
        fields = ['name', 'email', 'contact', 'password']
        widgets = {
            'password': forms.PasswordInput(),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm = cleaned_data.get("confirm_password")

        if password != confirm:
            self.add_error('confirm_password', "Passwords do not match")


class CustomerLoginForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-input',
        'placeholder': 'Enter your email',
        'required': True
    }))
    
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-input',
        'placeholder': 'Enter your password',
        'required': True
    }))

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'price', 'quantity', 'description', 'category', 'customized', 'image']

from django import forms
from .models import Seller

from django import forms
from .models import Seller


class SellerProfileForm(forms.ModelForm):
    class Meta:
        model = Seller   
        fields = [
            'full_name', 'username', 'dob',
            'experience', 'skills', 'city',
            'profile_image', 'additional_details'
        ]
