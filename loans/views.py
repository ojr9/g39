from django.views.generic import TemplateView


class LoanIndex(TemplateView):
    template_name = 'loans/index.html'
