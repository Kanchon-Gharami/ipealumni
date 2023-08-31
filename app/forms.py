from django import forms
from django.core.exceptions import ValidationError

from .models import MyCustomUser, Profile

class UserForm(forms.ModelForm):
    class Meta:
        model = MyCustomUser
        fields = ['first_name', 'last_name', 'email']


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = '__all__'
        exclude = ['user']
    
    # def clean_whatsapp_no(self):
    #     data = self.cleaned_data['whatsapp_no']
        
    #     # Remove any non-digit characters
    #     cleaned_data = ''.join(filter(str.isdigit, str(data)))

    #     # Check the length constraints
    #     if len(cleaned_data) < 10 or len(cleaned_data) > 15:
    #         raise ValidationError("Enter a valid WhatsApp number with 10 to 15 digits.")

    #     return cleaned_data
    

class ProfilePictureForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['profile_picture']

