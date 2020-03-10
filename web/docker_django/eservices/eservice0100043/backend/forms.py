from django import forms
from eservice0100043.models import EService0100043
from eservices.eservice0100043.forms import EServiceForm0100043


class EServiceBackendForm0100043(EServiceForm0100043):
    def __init__(self, *args, **kwargs):
        super(EServiceBackendForm0100043, self).__init__(*args, **kwargs)

    class Meta:
        model = EService0100043
        fields = [
            "title",
            "comment",
            "deadline",
            "type_license",
            "payment",
            "region",
            "city",

        ]
        widgets = {
            "title": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Короткий опис не більше 512 символів"
            }),
        }