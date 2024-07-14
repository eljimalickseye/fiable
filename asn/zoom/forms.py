from django import forms


class Upload(forms.Form):
    file = forms.FileField(label='Ajouter +')