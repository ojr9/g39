from django.shortcuts import render
from django.views.generic import DetailView, UpdateView, View
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Saver
from .forms import UpdateSaverForm
from payment.models import MangoNaturalUser
from cuenta.models import Cuenta


class SaverView(LoginRequiredMixin, DetailView):
    model = Saver
    template_name = 'saver/detail.html'
    context_object_name = 'saver'

    def get_object(self, queryset=None):
        obj = Saver.objects.get(user=self.request.user)
        return obj

    def get_context_data(self, **kwargs):
        context = super(SaverView, self).get_context_data()
        context['cuentas'] = Cuenta.objects.filter(user=self.request.user)
        if not self.object.mid == 0:
            context['docs'] = MangoNaturalUser.objects.get(user=self.request.user).get_docs_list()
        return context


class SaverUpdate(LoginRequiredMixin, UpdateView):
    model = Saver
    template_name = 'saver/update.html'
    fields = ['birthday', 'nationality', 'country_of_residence']
    # initial = how was this again?

    def get_object(self, queryset=None):
        obj = Saver.objects.get(user=self.request.user)
        return obj


class SaverUpdateMPNU(LoginRequiredMixin, UpdateView):
    model = MangoNaturalUser
    template_name = 'saver/update.html'
    form_class = UpdateSaverForm

    def get_object(self, queryset=None):
        obj = MangoNaturalUser.objects.get(user=self.request.user)
        return obj

    def form_valid(self, form):
        self.object.validate(document_type='IDENTITY_PROOF', front=self.request.FILES['front'],
                             back=self.request.FILES['back'])
        return super().form_valid(form)


# The idea is to make the validation request as a gen view class
# # This is incomplete and no idea if this will work or can be chucked.
# class UpdateValidate(LoginRequiredMixin, View):
#     def get(self, request):
#         saver = Saver.objects.get(user=request.user)
#         context = {}
#         if saver.validated:
#             context['validated'] = True
#         dataform = KYCNatUserDocs()
#         userform = ''
#         context['dataform'] = dataform
#         context['userform'] = userform
#         return render(request, 'saver/update.html', context)
#
#     def post(self, request):
#         mpu = MangoNaturalUser.object.get(user=request.user)
#         userform = Form(request.POST)
#         dataform = KYCNatUserDocs(files=request.FILES)
#         if userform.is_valid() and dataform.is_valid():
