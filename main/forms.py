from django import forms

class ricercaForm(forms.Form):
    text_search = forms.CharField(label='Cerca ricetta', max_length=100)

