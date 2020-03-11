from django import forms
from support.models import Message

class MessageForm(forms.ModelForm):
    text = forms.CharField(
        label='',
        max_length=1000,
        required=False,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'name': 'message', 'placeholder': 'Напишіть ваше повідомлення...'}
        )
    )
    file = forms.FileField(label='',required=False,widget=forms.FileInput(attrs={'class': 'hiddenfile', 'name':'upload'}))
    class Meta:
        model = Message
        fields = ('text', 'file')