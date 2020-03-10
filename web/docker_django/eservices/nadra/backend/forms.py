from django import forms
from nadra.models import NadraModel
from eservices.nadra.forms import NadraForm


class EServiceBackendFormNadra(NadraForm):
    def __init__(self, *args, **kwargs):
        super(EServiceBackendFormNadra, self).__init__(*args, **kwargs)

    class Meta:
        model = NadraModel
        fields = [
            'title',
            'comment',
            'deadline',

        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Короткий опис не більше 512 символів'}),
        }