from django import forms
from django.contrib.auth.models import User
from .models import Case, CaseUpdate
# from django.contrib.auth.forms import UserCreationForm

#for admin signup
class AdminSigupForm(forms.ModelForm):
    class Meta:
        model=User
        fields=['first_name','last_name','username','password']
        widgets = {
        'password': forms.PasswordInput()
        }

#for member signup
class MemberUserForm(forms.ModelForm):
    class Meta:
        model=User
        fields=['first_name','last_name','username','password']
        widgets = {
        'password': forms.PasswordInput()
        }

class CaseForm(forms.ModelForm):
    class Meta:
        model=Case
        fields=['title','description','location','image']

class CaseUpdateForm(forms.ModelForm):
    class Meta:
        model=CaseUpdate
        fields=['title','description','location','image']