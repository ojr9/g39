from django.shortcuts import render
from django.views.generic import CreateView, DetailView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Blog, Entry


class OwnerMixin:
    def get_queryset(self, request):
        qs = super(OwnerMixin, self).get_queryset()
        return qs.filter(user=request.user)


class BlogCreate(LoginRequiredMixin, CreateView):
    model = Blog
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.user = self.request.user


class EntryCreate(LoginRequiredMixin, CreateView):
    model = Entry
    template_name = 'blog/create.html'
