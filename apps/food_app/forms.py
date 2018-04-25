from django import forms
from django.forms import ModelForm
from .models import RestaurantImage
from .models import User
from django.core.exceptions import NON_FIELD_ERRORS
from django.contrib.auth.forms import UserCreationForm

class RestaurantForm(forms.ModelForm):
    class Meta:
        model = RestaurantImage
        fields = ('image',)

