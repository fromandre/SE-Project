from django import forms
from main.models import ricettario

class FormRicetta(forms.Form):
    def __init__(self, *args, **kwargs):
        ingredienti = kwargs.pop('ingredienti')
        super(FormRicetta, self).__init__(*args, **kwargs)
        counter = 1
        while counter <= ingredienti:
            self.fields['quantità' + str(counter)] = forms.CharField(label='Quantità '+str(counter))
            self.fields['ingrediente' + str(counter)] = forms.CharField(label='Ingrediente '+str(counter)) 
            counter += 1
    nome_ricetta = forms.CharField()
    procedimento_ricetta = forms.CharField(widget=forms.Textarea)
    immagine_ricetta = forms.FileField()
    ricettari = forms.ModelChoiceField(queryset = ricettario.objects.all(), to_field_name="name")
    
class NumeroCampi(forms.Form):
    campi = forms.IntegerField(max_value=30, label="Ingredienti")
    
class FormRicettario(forms.Form):
    name = forms.CharField()
    immagine = forms.FileField()

class SceltaRicettario(forms.Form):
    ricettari = forms.ModelChoiceField(queryset = ricettario.objects.all(), to_field_name="name")

