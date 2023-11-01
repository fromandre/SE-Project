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
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import pandas as pd

# Create your views here.

#Cosa mostra il sito

def cercaricetta(nomericerca):
    nomiricette = []
    queryset = ricetta.objects.none()
    vectorizer = TfidfVectorizer(ngram_range=(1,2))
    vector = ricetta.objects.all()
    for element in vector:
        nomiricette.append(element.nome)
    tfidf = vectorizer.fit_transform(nomiricette)
    query_vec = vectorizer.transform([nomericerca])
    simile = cosine_similarity(query_vec, tfidf).flatten()
    indici = np.argpartition(simile, -5)[-5:] #5 ric più simili 
    for element in indici:
        queryset |= (ricetta.objects.filter(nome = nomiricette[element]))
    return queryset

def collaborativefiltering(request):
    user = request.user
    queryset = Recensione.objects.none() #recensioni buone da utenti simili
    queryset2 = Recensione.objects.none() #recensioni da tutti gli utenti
    utenti = [] #utenti che hanno recensito le nostre stesse ricette
    ricettariutente = ricettario.objects.filter(user = user)
    allutenti = [] #lista tutti utenti
    allusernomiric = [] #nomi ricette valutate buone 
    nomiricsugg = [] #ricette suggerite 
    nomiricsalvate = []

    #ricette recensite dall'utente con più di 4 punti
    list = Recensione.objects.filter(user = user, punteggio__gte = 5)
        
    #recensioni di altri utenti sulle stesse ricette recensite da noi maggiori uguali a 4
    for element in list:
        recensionicomuni = Recensione.objects.filter(ricetta = element.ricetta, punteggio__gte = 4).exclude(user = user)
        for r in recensionicomuni:
            if r:
                if r.user not in utenti:
                    utenti.append(r.user) 
    
    #ricette valutate con più di 4 da utenti simili a noi
    for utente in utenti:
        queryset |= Recensione.objects.filter(user = utente, punteggio__gte = 4)
    for q in queryset:
        nomiricsugg.append(q.ricetta.nome)
        for ricettario_u in ricettariutente:
            temporaneo = ricetta.objects.filter(ricettario = ricettario_u)
            for t in temporaneo:
                if t.nome not in nomiricsalvate:
                    nomiricsalvate.append(t.nome)
        for nome in nomiricsalvate:
            if nome in nomiricsugg:
                nomiricsugg.remove(nome)

    index = pd.Index(nomiricsugg)
    #quante volte appare un film nella lista di recensioni degli utenti simili all'utente
    suggestions_utentisimili = index.value_counts() / len(utenti)
    suggestions_utentisimili = suggestions_utentisimili[suggestions_utentisimili > .10]

    #come sono valutate da TUTTI gli utenti le recensioni degli utenti simili a noi
    for o in queryset:
        queryset2 |= Recensione.objects.filter(ricetta = o.ricetta).exclude(user = user)
    for p in queryset2:
        allusernomiric.append(p.ricetta.nome)
        for nome in nomiricsalvate:
            if nome in allusernomiric:
                allusernomiric.remove(nome)
        if p.user not in allutenti:
            allutenti.append(p.user)
    index2 = pd.Index(allusernomiric)
    suggestions_tuttiutenti = index2.value_counts() / len(allutenti)
    sugg_percentuali = pd.concat([suggestions_utentisimili, suggestions_tuttiutenti], axis=1)
    sugg_percentuali.columns = ['simili', 'tutti']
    sugg_percentuali['punteggio'] = sugg_percentuali['simili'] / sugg_percentuali['tutti']
    sugg_percentuali = sugg_percentuali.sort_values('punteggio', ascending=False)
    ricette_suggerite =sugg_percentuali.head(5).index.tolist() # PRIME 5 RICETTE RACCOMANDATE PER L'UTENTE
    return ricette_suggerite
    
def valuta_ricetta(request):
     if request.method == "POST":
          user = request.user
          r_id = request.POST.get('r_id')
          val = request.POST.get('val')
          r_obj = ricetta.objects.get(id = r_id)
          if Recensione.objects.filter(ricetta = r_obj, user = user).exists():
               r = Recensione.objects.get(ricetta = r_obj, user = user)
               r.punteggio = val
               r.save()
          else: 
             rn = Recensione.objects.create(user = user, ricetta = r_obj, punteggio = val)
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
    s.ingredienti.clear()
    return redirect('listaspesa')

def scaricaricette(request):
    listaid = []
    primoget = "https://api.spoonacular.com/recipes/complexSearch?apiKey=395b53bbc5d446d9a7b43eb82f739384&number=100&offset=136"
    ric = requests.get(primoget).json()
    for element in ric['results']:
        listaid.append(element['id'])
    for numero in listaid:
        with reversion.create_revision():
            secondoget = "https://api.spoonacular.com/recipes/" + str(numero) + "/information?apiKey=395b53bbc5d446d9a7b43eb82f739384"
            ricettatmp = requests.get(secondoget).json()
            if ricettatmp['title']:
                nome = ricettatmp['title']
            else:
                nome = "Non disponibile"
            prontoin = ricettatmp['readyInMinutes']
            persone = ricettatmp['servings']
            if requests.get(ricettatmp['image']).content:
                img_data = requests.get(ricettatmp['image']).content
            else:
                img_data = "Non disponibile"
            path = "public/static/img/" + str(ricettatmp['id']) + ".jpg"
            file = open(path, 'wb')
            file.write(img_data)
            file.close()
            immagine = "img/" + str(ricettatmp['id']) + ".jpg"
            if ricettatmp['dishTypes']:
                portata = ricettatmp['dishTypes'][0]
            else:
                portata = "Non disponibile"
            if ricettatmp['analyzedInstructions']:
                istruzioni = ricettatmp['analyzedInstructions'][0]['steps']
                procedimento = ""
                for i in istruzioni:
                    passo = str(i['number']) + " " + i['step'] + "\n"
                    procedimento += passo
            else:
                procedimento = "Istruzioni non disponibili"
            salute = ricettatmp['healthScore']
            diet = ricettatmp['diets']
            diete = []
            for d in diet:
                diete.append(d)
            nuovaric = ricetta.objects.create(nome = nome, 
                                                    prontoin = prontoin,
                                                    persone = persone,
                                                    immagine = immagine,
                                                    portata = portata,
                                                    procedimento = procedimento,
                                                    punteggiosalute = salute,
                                                    tipidieta = str(diete)
                                                    )
            nuovaric.save()
            for ing in ricettatmp['extendedIngredients']:
                quant = str(ing['amount']) + ing['unit']
                ingrediente = IngredienteRicetta.objects.create(ingrediente = ing['nameClean'], 
                                                    quantità = quant)
                nuovaric.ingredienti.add(ingrediente)
            reversion.set_comment("Prima versione della ricetta - v1.0")
    return redirect("homepage")

def esplora(request):
    user = request.user
    recensioni = Recensione.objects.filter(user = user)
    counter = 0
    queryset = ricetta.objects.none()
    for r in recensioni:
        if r.punteggio == 5 and len(collaborativefiltering(request)) > 0:
            suggestions = collaborativefiltering(request)
            counter = 1
            for element in suggestions:
                queryset |= ricetta.objects.filter(nome = element)
    ricerca = SceltaRicettario(utente = user)
    if request.method == "POST" and request.POST['action'] == 'Salva':
        nome_ricettario = request.POST.get('ricettari')
        idric = request.POST.get('ricetta')
        tmp_ricettario = ricettario.objects.get(name = nome_ricettario)
        tmp_ric = ricetta.objects.get(id=idric)
        tmp_ric.ricettario.add(tmp_ricettario)
        return redirect("homepage")
    if request.method == "POST" and request.POST['action'] == 'Cerca':
        parola = request.POST.get('text_search')
        translated = GoogleTranslator(source='it', target='en').translate(text=parola)
        risultati = cercaricetta(translated)
        return render(request, "main/esplora.html", {'ricette': risultati, 'form': ricercaForm, 'formric': ricerca})
    ricette = ricetta.objects.all()
    return render(request, "main/esplora.html", {'ricette':ricette, 'suggestions':queryset,'numerosugg':list(range(1, queryset.__len__() + 1)), 'form':ricercaForm, 'formric': ricerca, 'counter':counter})
