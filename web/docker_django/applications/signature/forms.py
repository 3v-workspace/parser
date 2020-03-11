from django import forms
from .models import ServiceRequest


class ServiceRequestForm(forms.ModelForm):
    class Meta:
        model = ServiceRequest
        fields = ['first_name', 'last_name', 'birthday', 'phone']
    first_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control',
                                                               'style': 'margin-bottom: 10px;'}),
                                 label="Ім'я*:")
    last_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control',
                                                              'style': 'margin-bottom: 10px;'}),
                                label="Прізвище*:")
    birthday = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control',
                                                              'style': 'margin-bottom: 10px;',
                                                             'data-inputmask': "'alias': 'dd/mm/yyyy'"}),
                               required=True,
                               label="Дата народження*:")
    phone = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control',
                                                          'style': 'margin-bottom: 10px;',
                                                          'data-inputmask': '"mask": "+99(999) 999-99-99"',
                                                          'data-mask': '',
                                                          'modelClean': 'true'}),
                            required=True,
                            label="Номер телефону*:")
