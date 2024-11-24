from django import forms
from users.models import UserProfile


# User Profile Update Form
class UserProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['delivery_address', 'phone_number']
