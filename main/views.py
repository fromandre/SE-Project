from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from .models import *
from autenticazione.views import register
from .forms import ricercaForm
from ricette.forms import SceltaRicettario
import requests
import json
from json import loads as jsonloads
from deep_translator import GoogleTranslator


# Create your views here.

#Cosa mostra il sito

def estrai_ingr(ricetta_target):
    misura = []
    ingrediente = []
    ingr = {}
    for num in ricetta_target['meals'][0]:
            if num.startswith('strMeasure') and ricetta_target['meals'][0][num] != "" and ricetta_target['meals'][0][num] != None:
                misura.append(ricetta_target['meals'][0][num])
    for key in ricetta_target['meals'][0]:
        if key.startswith('strIngredient') and ricetta_target['meals'][0][key] != "" and ricetta_target['meals'][0][key] != None:
                ingrediente.append(ricetta_target['meals'][0][key])
    for ing in ingrediente:
         for val in misura:
              ingr[ing] = val
              misura.remove(val)
              break
    return ingr

def esplora(request):
    if request.user.is_authenticated:
        search = ricercaForm()
        if request.method == "POST":
            query = request.POST.get('text_search')
            translated = GoogleTranslator(source='it', target='en').translate(text=query)
            api_url = 'http://www.themealdb.com/api/json/v1/1/search.php?s='
            ricette = requests.get(api_url + translated).json()
            return render(request, "main/esplora_ricette.html", {"form": search, "ricette": ricette['meals']})
        else:
            api_url = 'http://www.themealdb.com/api/json/v1/1/categories.php?'
            categorie = requests.get(api_url).json()
            return render(request, "main/esplora.html", {"form": search, "lista_categorie": categorie})
    else:
        return redirect('register')
    
def esplora_cat(request, cat):
    search = ricercaForm()
    ricette = requests.get('http://www.themealdb.com/api/json/v1/1/filter.php?c=' + cat).json()
    return render(request, "main/esplora_ricette.html", {"form": search, "ricette": ricette['meals']})

def apri_ric (request, id):
    ricetta_info = requests.get('http://www.themealdb.com/api/json/v1/1/lookup.php?i=' + id).json()
    if request.method == "POST":
        nome_ricettario = request.POST.get('ricettari')
        tmp_ricettario = ricettario.objects.get(name = nome_ricettario)
        ingr = estrai_ingr(ricetta_info)
        ricetta_nome = ricetta_info['meals'][0]['strMeal']
        ricetta_descrizione = ricetta_info['meals'][0]['strInstructions']
        img_data = requests.get(ricetta_info['meals'][0]['strMealThumb']).content
        path = "public/static/img/" + ricetta_info['meals'][0]['idMeal'] + ".jpg"
        file = open(path, 'wb')
        file.write(img_data)
        file.close()
        ricetta_immagine = "img/" + ricetta_info['meals'][0]['idMeal'] + ".jpg"
        new_ricetta = ricetta(ricettario = tmp_ricettario, 
                            ricetta_nome = ricetta_nome, 
                            ricetta_descrizione = ricetta_descrizione, 
                            ricetta_immagine = ricetta_immagine)
        new_ricetta.save()
        new_recensione = Recensione(ricetta = new_ricetta, punteggio=0)
        new_recensione.save()
        print(new_ricetta.id)
        for chiave, valore in ingr.items():
            new_ingr = IngredienteRicetta(ricetta = new_ricetta.id, ingrediente = chiave, quantità = valore)
            new_ingr.save()
            new_ricetta.ricetta_ingredienti.add(new_ingr)
        return redirect('homepage')
    else:
        ingr = estrai_ingr(ricetta_info)
        return render(request, "analizza_ricetta.html", {"ricetta": ricetta_info['meals'][0], "ingredienti": ingr, "form": SceltaRicettario})

def valuta_ricetta(request):
     if request.method == "POST":
          r_id = request.POST.get('r_id')
          val = request.POST.get('val')
          r_obj = ricetta.objects.get(id = r_id)
          if Recensione.objects.filter(ricetta = r_obj).exists():
               r = Recensione.objects.get(ricetta = r_obj)
               r.punteggio = val
               r.save()
          else: 
             rn = Recensione.objects.create(ricetta = r_obj, punteggio = val)
             rn.save()    
          return JsonResponse({'success':'true', 'score':val}, safe=False, status = 200)
     return JsonResponse({'success':'false'}, status = 500)

def aggiungispesa(request):
    if request.method == "POST":
        user = request.user
        data = jsonloads(request.POST.get('dizionario'))
        for element in data:
            ingrediente = element
            quantità = data[element]
            ing = IngredienteRicetta.objects.get(ingrediente = ingrediente, quantità = quantità)
            if Spesa.objects.get_or_create(user = user):
                s = Spesa.objects.get_or_create(user=user)
                s[0].ingredienti.add(ing)
                s[0].save()
        a = Spesa.objects.get_or_create(user = user)
        s = a[0]
        queryset = s.ingredienti.all()
        for element in queryset: 
            print(element.ingrediente, element.quantità)   
        return JsonResponse({'success':'true'}, safe=False, status=200)

def listaspesa(request):
    user = request.user
    s = Spesa.objects.get_or_create(user = user)
    queryset = s[0].ingredienti.all()
    numero = 0
    dic = {}
    for el in queryset:
        dic[el.ingrediente] = el.quantità
        numero += 1
    return render (request, "main/listaspesa.html", {"numero": numero, "spesa": dic})
     
def puliscispesa(request):
    user = request.user
    s = Spesa.objects.get(user = user)
    queryset = s.ingredienti.clear()
    return redirect('listaspesa')