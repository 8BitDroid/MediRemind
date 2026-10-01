from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Medicine


class UserRegistrationForm(UserCreationForm):
    """Extended user registration form with email and name fields."""

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email',
            'id': 'register-email',
        })
    )
    first_name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your first name',
            'id': 'register-first-name',
        })
    )
    last_name = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your last name',
            'id': 'register-last-name',
        })
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Choose a username',
            'id': 'register-username',
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Create a password',
            'id': 'register-password1',
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm your password',
            'id': 'register-password2',
        })

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user


class MedicineForm(forms.ModelForm):
    """Form for adding/editing a medicine schedule."""

    class Meta:
        model = Medicine
        fields = [
            'name', 'dosage', 'frequency', 'meal_instruction',
            'time_slot_1', 'time_slot_2', 'time_slot_3',
            'start_date', 'end_date', 'notes', 'image', 'is_active'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Medicine name (e.g., Paracetamol)',
                'id': 'medicine-name',
            }),
            'dosage': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 500mg, 1 tablet',
                'id': 'medicine-dosage',
            }),
            'frequency': forms.Select(attrs={
                'class': 'form-select',
                'id': 'medicine-frequency',
            }),
            'meal_instruction': forms.Select(attrs={
                'class': 'form-select',
                'id': 'medicine-meal',
            }),
            'time_slot_1': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time',
                'id': 'medicine-time1',
            }),
            'time_slot_2': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time',
                'id': 'medicine-time2',
            }),
            'time_slot_3': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time',
                'id': 'medicine-time3',
            }),
            'start_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'id': 'medicine-start-date',
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'id': 'medicine-end-date',
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Any special instructions...',
                'id': 'medicine-notes',
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
                'capture': 'environment',
                'id': 'medicine-image',
                'onchange': 'previewImage(this)',
            }),

            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'id': 'medicine-active',
            }),
        }

