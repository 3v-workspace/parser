from django import forms

from document_66666666666.forms import DocumentForm66666666666
from document_66666666666.models import Document_66666666666


class DocumentFrontendForm66666666666(DocumentForm66666666666):
    def __init__(self, *args, **kwargs):
        super(DocumentFrontendForm66666666666, self).__init__(*args, **kwargs)

    class Meta:
        model = Document_66666666666
        fields = [
            'title',
            'comment',
            'deadline',
            'type_license',
            'payment',
            'region',
            'city',
            'file',

        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Короткий опис не більше 512 символів'}),
        }