from django.contrib.auth import views as auth_views
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse_lazy
from django.contrib.auth.views import PasswordResetConfirmView
from django.shortcuts import render, redirect   
from .forms import CustomUserCreationForm, CustomPasswordResetForm
from django import forms
from django.contrib.auth.forms import SetPasswordForm
from django.utils.translation import gettext_lazy as _
from .models import CustomUser
from django.views.generic.edit import FormView
from django.views import generic
from django.contrib.auth import get_user_model
User = get_user_model()

class RegisterView(FormView):
    form_class = CustomUserCreationForm
    template_name = 'registro.html'
    success_url = reverse_lazy('usuario:login')

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            form.save()
            return redirect('usuario:login')
        return render(request, self.template_name, {'form': form})

class LoginView(auth_views.LoginView):
    template_name = 'login.html'

class LogoutView(auth_views.LogoutView):
    pass

class CustomPasswordResetView(FormView):
    template_name = 'password_reset.html'
    form_class = CustomPasswordResetForm
    success_url = reverse_lazy('password_reset_done')

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['uidb64'] = self.kwargs['uidb64']
        context['token'] = self.kwargs['token']
        return context

    def form_invalid(self, form):
        form.add_error('new_password2', 'Las contraseñas no coinciden.')
        return self.render_to_response(self.get_context_data(form=form))

class PasswordResetView(auth_views.PasswordResetView):
    template_name = 'password_reset.html'
    success_url = reverse_lazy('usuario:password_reset_done')
    email_template_name = 'password_reset_email.html'
    html_email_template_name = None
    
    def form_valid(self, form):
        # Obtener los valores uidb64 y token de la respuesta
        response = super().form_valid(form)
        uidb64 = urlsafe_base64_encode(force_bytes(form.cleaned_data['email']))
        token = default_token_generator.make_token(form.user_cache)
        # Imprimir los valores de uidb64 y token
        print("uidb64:", uidb64)
        print("token:", token)
        # Incluir los valores en el contexto
        self.request.session['reset_password'] = {
            'uidb64': uidb64,
            'token': token,
        }
        return response


class PasswordResetDoneView(auth_views.PasswordResetDoneView):
    template_name = 'password_reset_done.html'
    
class PasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    template_name = 'password_reset_complete.html'
