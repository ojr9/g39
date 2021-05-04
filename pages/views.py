from django.shortcuts import render
from django.views.generic import TemplateView
# from django.contrib.auth.forms import UserCreationForm


class Index(TemplateView):
    template_name = 'pages/index.html'


class ToDo(TemplateView):
    template_name = 'pages/todo.html'


class TermsAndConditions(TemplateView):
    template_name = 'pages/terms.html'


# This was replaced by the allauth package
# class UserSignUp(TemplateView):
#     template_name = 'registration/signup.html'
#     extra_context = {'form': UserCreationForm}
