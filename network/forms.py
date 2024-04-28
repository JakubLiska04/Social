from django import forms
from .models import Order, JobListing, Application, Event, Profile
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

class SignupForm(UserCreationForm):
    email = forms.EmailField(max_length=254, help_text='Required. Enter a valid email address.')

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class SigninForm(AuthenticationForm):
    class Meta:
        model = User
        fields = ['username', 'password']
        
class PaymentForm(forms.Form):
    amount = forms.DecimalField(max_digits=10, decimal_places=2)
    payment_date = forms.DateTimeField()


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['service_name', 'description']


class JobListingForm(forms.ModelForm):
    class Meta:
        model = JobListing
        fields = ['title', 'description', 'company',
                  'location', 'skills_required', 'salary']


class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['resume', 'cover_letter']


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'start_date', 'end_date', 'description']


class ProfilePicForm(forms.ModelForm):
    profile_image = forms.ImageField(label="Profile Picture")

    class Meta:
        model = Profile
        fields = ['profile_image']
