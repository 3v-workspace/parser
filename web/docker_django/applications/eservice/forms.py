from django import forms
from eservice.models import EServiceStar
from django.forms import Form


class DocumentStarForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(DocumentStarForm, self).__init__(*args, **kwargs)
        self.fields['comment'].label = "Ваш коментар по наданню послуги"
        self.fields['comment'].attrs = {'class': 'textarea_md'}

    quality = forms.FloatField(label="Якість наданої послуги", required=False, max_value=10,
                               min_value=0, widget=forms.NumberInput(attrs={'id': 'quality'}))
    easy_ordering = forms.FloatField(label="Легкість замовлення послуги", required=False, max_value=10,
                                     min_value=0, widget=forms.NumberInput(attrs={'id': 'easy_ordering'}))
    term_service = forms.FloatField(label="Строк надання послуги", required=False, max_value=10,
                                    min_value=0, widget=forms.NumberInput(attrs={'id': 'term_service'}))
    comment = forms.TextInput(attrs={'class': 'textarea_md'})

    class Meta:
        model = EServiceStar
        fields = [
            'quality',
            'easy_ordering',
            'term_service',
            'comment',
        ]