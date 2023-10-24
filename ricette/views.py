from django.shortcuts import render, redirect
from django.shortcuts import HttpResponse
from django.http import HttpResponseRedirect
from .forms import FormRicetta, FormRicettario, NumeroCampi, FormEdit, FormIngr, FormCheckIngr
from django.contrib.staticfiles import finders
from .models import * 
from reversion.models import Version
import requests

# Create your views here.
def numerocampi(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            return redirect('ricette/' + request.POST.get('campi'))
        else:
            return render(request, 'numerocampi.html', {'form': NumeroCampi})
     
def crea_ricetta(request, campi):
    if request.user.is_authenticated:
        user = request.user
        if request.method == "POST":
            counter = 1
            data = request.POST
            nome_ricetta = data.get('nome_ricetta')
            descrizione_ricetta = data.get('procedimento_ricetta')
            immagine_ricetta = request.FILES.get('immagine_ricetta')
            ricettario_tmp = ricettario.objects.get(name = data.get('ricettari'))
            prontoin = data.get('prontoin')
            persone = data.get('persone')
            portata = data.get('portata')
            punteggiosalute = data.get('punteggiosalute')
            tipidieta = data.get('tipidieta')
            newricetta = ricetta.objects.create(nome = nome_ricetta, 
                                                prontoin = prontoin,
                                                persone= persone,
                                                immagine = immagine_ricetta,
                                                portata= portata,
                                                procedimento = descrizione_ricetta,
                                                punteggiosalute = punteggiosalute,
                                                tipidieta = tipidieta)
            newricetta.save()
            newricetta.ricettario.add(ricettario_tmp)
            newrating = Recensione(ricetta = newricetta, punteggio=0)
            newrating.save()
            while counter <= int(campi):
                quantità_tmp = data.get('quantità' + str(counter))
                ingrediente_tmp = data.get('ingrediente' + str(counter))
                ing_tmp = IngredienteRicetta(ingrediente=ingrediente_tmp, quantità=quantità_tmp)
                ing_tmp.save()
                newricetta.ingredienti.add(ing_tmp)
                counter += 1
            return redirect("homepage")
        else:
            ricettan = FormRicetta(ingredienti = int(campi), utente = user)
            return render(request, 'crea_ricetta.html', {"form": ricettan})
    else:
        return redirect('register')

def elimina_ricetta(request, id):
    if request.user.is_authenticated:
        queryset = ricetta.objects.get(id = id)
        queryset.delete()
        return redirect('gestioneric')

def visual_ricetta(request, id):
    if request.user.is_authenticated:
        user = request.user
        ric = ricetta.objects.get(id = id)
        ingr = ric.ingredienti.all()
        if Recensione.objects.filter(ricetta = ric, user = user).exists():
            val = Recensione.objects.get(ricetta=ric, user = user).punteggio
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
        ric = ricettario.objects.get(id=idricettario)
        if ric.ricetta_set.all():
            queryset = ric.ricetta_set.all()
        else:
            queryset = []
        return render(request, 'visual_ricettario.html', {"ricette": queryset})
        
def elimina_ricettario(request, id):
    if request.user.is_authenticated:
        request.user.ricettario.get(id = id).delete()
        return redirect('gestioneric')
    
def proponimodifica(request, id):
    with reversion.create_revision():
        if request.method == "POST" and request.POST['action'] == 'aggingr':
            ing = IngredienteRicetta.objects.create(quantità = request.POST.get('quantità'), ingrediente = request.POST.get('ingrediente'))
            ri = ricetta.objects.get(id = id)
            ing.save()
            ri.ingredienti.add(ing)
            ri.save()
            print(ing, "Salvato")
            reversion.set_user(request.user)
            reversion.set_comment("Aggiunto ingrediente " + ing.ingrediente + " dall'utente " + str(request.user))
            return HttpResponseRedirect(request.path_info)
        if request.method == "POST" and request.POST['action'] == 'eliminaingr':
            lista = request.POST.getlist('ingredienti')
            for elemento in lista:
                tmp = IngredienteRicetta.objects.get(id = elemento)
                r = ricetta.objects.get(id = id)
                r.ingredienti.remove(tmp)
                r.save()
            reversion.set_user(request.user)
            reversion.set_comment("Rimossi " + str(len(lista)) +" ingredienti dall'utente " + str(request.user))
            return HttpResponseRedirect(request.path_info)
        if request.method == "POST" and request.POST['action'] == 'salvamodifiche':
            nome = request.POST.get('nome')
            portata = request.POST.get('portata')
            procedimento = request.POST.get('procedimento')
            punteggiosalute = request.POST.get('punteggiosalute')
            tipidieta = request.POST.get('tipidieta')
            rtmp = ricetta.objects.get(id = id)
            rtmp.nome = nome
            rtmp.portata = portata
            rtmp.procedimento = procedimento
            rtmp.punteggiosalute = punteggiosalute
            rtmp.tipidieta = tipidieta
            rtmp.save()
            reversion.set_user(request.user)
            reversion.set_comment("Aggiornati campi testuali dall'utente " + str(request.user))
            return redirect("homepage")
    r = ricetta.objects.get(id=id)
    versions = Version.objects.get_for_object(r) 
    return render(request, 'proponimodifica.html', {'ricetta': r, 'formricetta': FormEdit(instance = r), 'formingr': FormIngr(), 'formcheckingr': FormCheckIngr(r = r), 'versioni' : versions})

def vecchiaversione(request, id):
    vecchia = Version.objects.get(id = id)
    r = vecchia._object_version.object
    ing = vecchia.field_dict["ingredienti"]
    ingredienti = []
    for i in ing:
        ingredienti.append(IngredienteRicetta.objects.get(id = i))
    return render(request, 'vecchiaversione.html', {'ricetta': r, 'versione': vecchia, 'ingredienti': ingredienti})
