from django.shortcuts import render, redirect
from django.shortcuts import HttpResponse
from .forms import FormRicetta, FormRicettario, NumeroCampi
from django.contrib.staticfiles import finders
from .models import *
import requests

# Create your views here.
def numerocampi(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            return redirect('ricette/' + request.POST.get('campi'))
        else:
            return render(request, 'numerocampi.html', {'form': NumeroCampi})
     
def ricette(request, campi):
    if request.user.is_authenticated:
        if request.method == "POST":
            counter = 1
            data = request.POST
            nome_ricetta = data.get('nome_ricetta')
            descrizione_ricetta = data.get('procedimento_ricetta')
            immagine_ricetta = request.FILES.get('immagine_ricetta')
            ricettario_tmp = ricettario.objects.get(name = data.get('ricettari'))
            newricetta = ricetta.objects.create(ricettario = ricettario_tmp, ricetta_nome = nome_ricetta, ricetta_descrizione = descrizione_ricetta, ricetta_immagine = immagine_ricetta)
            newricetta.save()
            newrating = Recensione(ricetta = newricetta, punteggio=0)
            newrating.save()
            while counter <= int(campi):
                quantità_tmp = data.get('quantità' + str(counter))
                ingrediente_tmp = data.get('ingrediente' + str(counter))
                ing_tmp = IngredienteRicetta(ingrediente=ingrediente_tmp, quantità=quantità_tmp)
                ing_tmp.save()
                newricetta.ricetta_ingredienti.add(ing_tmp)
                counter += 1
            return redirect("homepage")
        else:
            return render(request, 'crea_ricetta.html', {"form": FormRicetta(ingredienti=int(campi))})
    else:
        return redirect('register')

def elimina_ricetta(request, id):
    if request.user.is_authenticated:
        queryset = ricetta.objects.get(id = id)
        queryset.delete()
        return redirect('gestioneric')

def visual_ricetta(request, id):
    if request.user.is_authenticated:
        ric = ricetta.objects.get(id = id)
        ingr = ric.ricetta_ingredienti.all()
        if Recensione.objects.filter(ricetta = ric).exists():
            val = Recensione.objects.get(ricetta=ric).punteggio
        else: 
            val = 0
        return render(request, 'visual_ricetta.html', {"ricetta": ric, "ingredienti": ingr, "rating": val})

def crea_ricettario(request):
    if request.user.is_authenticated:
        if request.method=="POST":
            data = request.POST
            name = data.get('name')
            immagine = request.FILES.get('immagine')
            new_ricettario = ricettario(name = name, immagine = immagine)
            request.user.ricettario.add(new_ricettario, bulk=False)
            return redirect("/homepage")
        else:
            return render(request, 'crea_ricettario.html', {'form': FormRicettario})
        
def gestione_ricettari(request):
    if request.user.is_authenticated:
        queryset = ricettario.objects.all()
        return render(request, 'gestione_ricettari.html', {'ricettario':queryset})
    
def visual_ricettario(request, idricettario):
    if request.user.is_authenticated:
        queryset = ricetta.objects.filter(ricettario = idricettario)
        return render(request, 'visual_ricettario.html', {"ricette": queryset})
        
def elimina_ricettario(request, id):
    if request.user.is_authenticated:
        request.user.ricettario.get(id = id).delete()
        return redirect('gestioneric')