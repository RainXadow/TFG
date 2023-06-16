from django import forms
from .models import Post
from django.core.validators import MinValueValidator, MaxValueValidator

class PostCreateForm(forms.ModelForm):
    evaluation = forms.DecimalField(validators=[MinValueValidator(0), MaxValueValidator(5)], decimal_places=1, max_digits=3)

    class Meta:
        model = Post
        fields = ['title', 'content', 'evaluation', 'image', 'price', 'where_to_find']
        widgets = {
            # Tus otros widgets aquí
            'evaluation': forms.NumberInput(attrs={'readonly': 'readonly', 'step': '0.1'}),
        }


class PostUpdateForm(forms.ModelForm):
    evaluation = forms.DecimalField(validators=[MinValueValidator(0), MaxValueValidator(5)], decimal_places=1, max_digits=3)

    class Meta:
        model = Post
        fields = ['title', 'content', 'evaluation', 'image', 'price', 'where_to_find']
        widgets = {
            # Tus otros widgets aquí
            'evaluation': forms.NumberInput(attrs={'step': '0.1'}),
            #'image': forms.HiddenInput(),
        }
        