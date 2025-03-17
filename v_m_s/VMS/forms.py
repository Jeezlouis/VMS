from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Visitor, Asset, VisitorPreRegistration
import re


class CustomUserCreationForm(UserCreationForm):
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Enter a strong password",
        }),
        
    )

    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Confirm your password",
        }),
    )

    class Meta:
        model = CustomUser
        fields = ["username", "email", "password1", "password2", "role"]
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter username"}),
            "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "Enter email address"}),
            "role": forms.Select(attrs={"class": "form-control"}),
        }

    # def clean_password1(self):
    #     password = self.cleaned_data.get("password1")
    #     if not re.search(r"^(?=.*[A-Z])(?=.*\d).{8,}$", password):
    #         raise forms.ValidationError(
    #             "Password must be at least 8 characters long, contain at least one capital letter, and include at least one number."
    #         )
    #     return password


class VisitorForm(forms.ModelForm):
    class Meta:
        model = Visitor
        fields = ["full_name", "email", "phone_number", "company_name", "purpose_of_visit"]
        widgets = {
            "full_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter full name"}),
            "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "Enter email address"}),
            "phone_number": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter phone number"}),
            "company_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter company name (optional)"}),
            "purpose_of_visit": forms.Textarea(attrs={"class": "form-control", "rows": 4, "placeholder": "Describe purpose of visit"}),
        }


class AssetForm(forms.ModelForm):
    class Meta:
        model = Asset
        fields = ["name", "category", 'status', 'assigned_to']
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter asset name"}),
            "category": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter asset category"}),
            "assigned_to": forms.Select(attrs={"class": "form-control"}),
        }


class VisitorPreRegistrationForm(forms.ModelForm):
    class Meta:
        model = VisitorPreRegistration
        fields = ["name", "email", "purpose", "host"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter visitor name"}),
            "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "Enter visitor email"}),
            "purpose": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Enter purpose of visit"}),
            "host": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter host name"}),
        }
