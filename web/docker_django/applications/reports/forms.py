from django import forms
from django.forms import ChoiceField
from django.apps import apps
from eservice.models import EServiceType
from eservice0100043.models import EService0100043
from eservice0100044.models import EService0100044
from client_api.models import ClientApiEService, ClientApiEServiceField


class ClientApiEServiceForm(forms.ModelForm):
    eservice = forms.ModelChoiceField(queryset=EServiceType.objects.all(),
                                      widget=forms.Select(attrs={'id': "eservice", 'class': "exercise", 'onChange': 'js_admin_change(this)'}))

    class Media:
        js = (
            '//ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js',
            'js/admin_ajax.js',
        )

    class Meta:
        model = ClientApiEService
        exclude = []


class ChoiceFieldNoValidation(ChoiceField):
    def validate(self, value):
        pass


def validate_all_choices(value):
    # here have your custom logic
    pass


class ClientApiEServiceFieldForm(forms.ModelForm):

    def __init__(self,  *args, **kwargs):
        super(ClientApiEServiceFieldForm, self).__init__(*args, **kwargs)

        fields = [f.name for f in EService0100043._meta.get_fields()]

        models_list = []

        if self.instance.pk:
            obj_field = ClientApiEServiceField.objects.get(pk=self.instance.pk)

            eservice_model = obj_field.client_api_eservice.eservice.model
            apps_doc = obj_field.client_api_eservice.eservice.controller

            model = apps.get_model(apps_doc, eservice_model)
            models_list.append(model)

            field_list = []
            for item_models in models_list:
                for f in item_models._meta.get_fields():
                    if hasattr(f, 'verbose_name'):
                        field_list.append((f.name, f.verbose_name))

            self.fields['field'].choices = field_list
        else:
            field_list = []

            models_list = [EService0100043, EService0100044]

            for item_models in models_list:
                for f in item_models._meta.get_fields():
                    if hasattr(f, 'verbose_name'):
                        # print(f.verbose_name)
                        field_list.append((f.name, f.verbose_name))

            self.fields['field'].choices = field_list

    field = ChoiceFieldNoValidation(widget=forms.Select(attrs={'class': "doc_field", 'id': 'field_value', 'onfocus': 'js_admin_change_field(this)'}))

    class Media:
        js = (
            '//ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js',
            'js/admin_ajax.js',
        )

    class Meta:
        model = ClientApiEServiceField
        exclude = []