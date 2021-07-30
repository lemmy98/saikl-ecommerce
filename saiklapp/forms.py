from django.forms import ModelForm
from django import forms
from django.contrib.auth.forms import PasswordChangeForm, PasswordResetForm, UserCreationForm
from django.contrib.auth.models import User



from .models import *

class CustomerForm(ModelForm):
    class Meta:
        model = Customer
        fields = '__all__'
        exclude = ['user', 'date_created']

class OrderForm(ModelForm):
    class Meta:
        model = Order
        fields = '__all__'
        exclude = ['product']

class ProductForm(ModelForm):
    class Meta:
        model = Product
        fields = '__all__'


class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username','email','password1','password2']  

class FeedbackForm(ModelForm):
    class Meta:
        model = Feedback
        fields = '__all__'
        exclude = ['user']


class PasswordForgotForm(forms.Form):
    email = forms.CharField(widget=forms.EmailInput(attrs={
        "class": "form-control",
        "placeholder": "Enter your Email"
    }))
    def clean_email(self):
        e = self.cleaned_data.get("email")
        if Customer.objects.filter(user__email=e).exists():
            pass 
        else:
            raise forms.ValidationError("Customer with this account does not exist..")
        return e


class PasswordResetForm(forms.Form):
    new_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class':'form-control',
        'autocomplete': 'New Password',
        'placeholder':'Enter New Password',
    }), label="New Password")
    confirm_new_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class':'form-control',
        'autocomplete': 'New Password',
        'placeholder':'Enter New Password',
    }), label="New Password")

    def clean_confirm_new_password(self):
        new_password = self.cleaned_data.get("new_password")
        confirm_new_password = self.cleaned_data.get("confirm_new_password")
        if new_password != confirm_new_password:
            raise forms.ValidationError(
            "New Passwords did not match!"
        )
        return confirm_new_password


