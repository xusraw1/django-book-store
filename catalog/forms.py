# catalog/forms.py
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Order, Profile

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Имя пользователя",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [
            'first_name', 'middle_name', 'last_name', 'phone', 'whatsapp',
            'email', 'address', 'city', 'region', 'postal_code',
        ]
        widgets = {
            'address': forms.Textarea(attrs={'rows': 2}),
        }

class DeliveryPaymentForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['delivery_method', 'payment_method']

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['phone', 'address', 'city', 'avatar']