from django import forms
from .models import UserProfile

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['mobile_number', 'address', 'state', 'gender', 'country', 'pincode']
