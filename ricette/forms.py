from django import forms
from django.forms import ModelForm
from main.models import *

class FormRicetta(forms.Form):
    def __init__(self, *args, **kwargs):
        ingredienti = kwargs.pop('ingredienti')
        utente = kwargs.pop('utente')
        super(FormRicetta, self).__init__(*args, **kwargs)
        counter = 1
        self.fields['ricettari'] = forms.ModelChoiceField(queryset = ricettario.objects.filter(user = utente), to_field_name="name")
        while counter <= ingredienti:
            self.fields['quantità' + str(counter)] = forms.CharField(label='Quantità '+str(counter))
            self.fields['ingrediente' + str(counter)] = forms.CharField(label='Ingrediente '+str(counter)) 
            counter += 1
    nome_ricetta = forms.CharField()
    procedimento_ricetta = forms.CharField(widget=forms.Textarea)
    immagine_ricetta = forms.FileField()
    prontoin = forms.IntegerField()
    persone = forms.IntegerField()
    portata = forms.CharField()
    punteggiosalute = forms.IntegerField(min_value=0, max_value=100)
    tipidieta = forms.CharField()
    
    
class NumeroCampi(forms.Form):
    campi = forms.IntegerField(max_value=30, label="Ingredienti")
    
class FormRicettario(forms.Form):
    name = forms.CharField()
    immagine = forms.FileField()

class SceltaRicettario(forms.Form):
    def __init__(self,*args,**kwargs):
        self.utente = kwargs.pop('utente')
        super(SceltaRicettario,self).__init__(*args,**kwargs)
        self.fields['ricettari'] = forms.ModelChoiceField(queryset = ricettario.objects.filter(user = self.utente), to_field_name="name")
        self.fields['ricetta'] = forms.CharField(
            max_length=10,
            widget=forms.TextInput(attrs={'readonly': 'readonly'})
            )

class FormEdit(ModelForm):
    class Meta:
        model = ricetta
        fields = ["nome", "portata", "procedimento", "punteggiosalute", "tipidieta"]

class FormCheckIngr(forms.Form):
    def __init__(self, *args, **kwargs):
        self.r = kwargs.pop('r')
        super(FormCheckIngr, self).__init__(*args, **kwargs)
        self.fields['ingredienti'].queryset = self.r.ingredienti.all()

    ingredienti = forms.ModelMultipleChoiceField(
        queryset= None,
        widget=forms.CheckboxSelectMultiple(attrs={
            'class' : 'form-check-input'
        }))
    fields = ["ingredienti"]

class FormIngr(ModelForm):
    class Meta:
        model = IngredienteRicetta
        fields = ["quantità", "ingrediente"]