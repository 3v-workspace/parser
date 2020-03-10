from django import forms
from nadra.models import NadraModel

from eservices.nadra.forms import NadraForm


class EServiceFrontendFormNadra(NadraForm):
    def __init__(self, *args, **kwargs):
        super(EServiceFrontendFormNadra, self).__init__(*args, **kwargs)

    class Meta:
        model = NadraModel
        fields = [
            'pib',
            'inn',
            'title',
            'organ',
            'deadline',
            'place',
            'email',
            'phone',
            'info_person',
            'info_document',
            # 'comment',
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Короткий опис не більше 512 символів'}),
            'organ': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'напр. Виконавчий комітет Здолбунівської районної ради'}),
            'place': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Місцезнаходження'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ваш номер'}),
            'email': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ваш email'}),
            'info_person': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'посада та ПІБ'}),
            'info_document': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'напр. Статуту'}),
        }