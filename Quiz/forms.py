"""
Author:
Susan Wagle
"""
import re
from django import forms
from django.contrib.auth.models import User
from django.forms import PasswordInput


# defining a form for user registration
class UserRegistrationForm(forms.ModelForm):
    # Field for password input
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User  # Using the User model from Django's authentication system
        fields = (
            'username',  # Username field
            'email',  # email field
            'password'  # password field
        )
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Enter Username'}),
            'email': forms.TextInput(attrs={'placeholder': 'Enter Email', 'required': True, 'type': 'email'}),
        }

    def __init__(self, *args, **kwargs):
        super(UserRegistrationForm, self).__init__(*args, **kwargs)
        self.fields['password'].widget = PasswordInput(
            attrs={'placeholder': 'Enter Password'})

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if password:
            # regex for password
            pattern = r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$#%^&*!~])[A-Za-z\d@$#%^&*!~]{8,}$'
            if not re.match(pattern, password):
                raise forms.ValidationError(
                    "Password must be at least 8 characters long and contain letters, symbols and numbers."
                    # error message for invalid password.
                )
        return password  # Custom password validation


# Defining the form for user login
class UserLoginForm(forms.Form):
    email = forms.CharField(widget=forms.HiddenInput(),
                            required=False)  # hide the email field
    username = forms.CharField(required=True)  # username field
    password = forms.CharField(
        widget=forms.PasswordInput, required=True)  # password field

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update(
            {'placeholder': 'Enter Username'})  # Adding placeholder for the username
        self.fields['password'].widget = PasswordInput(
            attrs={'placeholder': 'Enter Password'})
