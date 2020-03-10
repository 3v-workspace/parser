from django import forms
from eservice.models import GeoCity
from eservice.models import EServiceMeta


class NadraForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(NadraForm, self).__init__(*args, **kwargs)

    pib = forms.CharField(label="ПІБ*:",  required=False,
                           widget=forms.TextInput(attrs={'class': 'form-control width_100', 'disabled': 'disabled'}))
    inn = forms.CharField(label="ПІБ*:", required=False,
                          widget=forms.TextInput(attrs={'class': 'form-control width_100', 'disabled': 'disabled'}))
    deadline = forms.DateField(required=False, widget=forms.DateInput(attrs={'class': "form-control datepicker", 'id':'dateMask',

                                                                             'placeholder': "Введіть кінечну дату вхідного послуги у форматі день/місяць/рік"}))
    # comment = forms.TextInput()
    #
    # type_license = forms.ModelChoiceField(empty_label='Оберіть тип ліцензії', label="Тип ліцензії*:",
    #                                       queryset=EServiceMeta.objects.get(category_index="1.0").get_children(),
    #                                       required=True, widget=forms.Select(
    #         attrs={'class': 'form-control select_e_driver ', }))
    #
    # payment = forms.ModelChoiceField(empty_label='Оберіть тип оплати', label="Оплата*:",
    #                                  queryset=EServiceMeta.objects.get(category_index="2.0").get_children(),
    #                                  required=True, widget=forms.Select(
    #         attrs={'class': 'form-control select_e_driver ', }))
    #
    # region = forms.ModelChoiceField(empty_label='Оберіть область', label="Область*:",
    #                                 queryset=GeoCity.objects.filter(parent=None),
    #                                 required=True, widget=forms.Select(
    #         attrs={'class': 'form-control select_e_driver ', }))
    #
    # city = forms.CharField(label="Місто*:", initial="Оберіть місто", required=True,
    #                        widget=forms.TextInput(attrs={'class': 'form-control width_100', 'disabled': 'disabled'}))

    file = forms.FileField(required=False, widget=forms.FileInput(attrs={'multiple': "true", 'id': 'my-file-selector', 'style': 'display:none',
                                                         'onchange': 'file_name(this)'}))