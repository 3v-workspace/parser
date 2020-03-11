from django import forms
from django.utils.translation import ugettext_lazy as _

from .models import *


class ChangeManagerForm(forms.Form):
    manager = forms.ModelChoiceField(queryset=User.objects.all()[:100],
                                     label=_('Manager'))

    def __init__(self, *args, **kwargs):
        self.department = kwargs.pop('department')
        super(ChangeManagerForm, self).__init__(*args, **kwargs)

    def save(self):
        new_manager = self.cleaned_data['manager']

        DeptManager.objects.filter(
            department=self.department
        ).set(
            department=self.department,
            employee=new_manager
        )


class ChangeTitleForm(forms.Form):
    position = forms.CharField(label=_('Position'))

    def __init__(self, *args, **kwargs):
        self.employee = kwargs.pop('employee')
        super(ChangeTitleForm, self).__init__(*args, **kwargs)

    def save(self):
        new_title = self.cleaned_data['position']

        # fixme: model Title missing
        Title.objects.filter(
            employee=self.employee,
        ).set(
            employee=self.employee,
            title=new_title
        )

