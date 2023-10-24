import os, sys
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'site_test.settings')
django.setup()
from django.test import TestCase, Client
from django.contrib.auth.models import User
from autenticazione.forms import RegisterForm
from django.contrib.auth import SESSION_KEY
from django.urls import reverse, resolve
from django.http import JsonResponse
from django.shortcuts import redirect
from unittest import mock
from django.core.files import File
import json
import pytest
from pytest_django.asserts import assertTemplateUsed
from autenticazione import views as a
from main import views as m 
from ricette import views as r
from chat import views as c
from ricette.forms import * 
from main.models import ricetta, ricettario, IngredienteRicetta, Recensione, Spesa
from chat.models import Group, Message
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import pandas as pd
import requests


# Create your tests here. CHECKED
class test_autenticazione_views_post(TestCase):
    def setUp(self):
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.utente = {'email':'usertest@gmail.com', 'username':'usertest', 'password1':'testpassword123', 'password2':'testpassword123'}
        self.client = Client()


    def test_registerview_POST(self):
            form = RegisterForm(data = {'email':'usertest@gmail.com', 'username':'usertest', 'password1':'testpassword123', 'password2':'testpassword123'})
            self.assertTrue(form.is_valid())
            response = self.client.post(self.register_url, self.utente)
            self.assertEqual(response.status_code, 302)

    def test_registerview_notauth(self):
         response = self.client.get(self.register_url)
         self.assertEqual(response.status_code, 200)
         self.assertTemplateUsed(response, 'registration/register.html')

    def test_registerview_autenticato(self):
        self.client.force_login(User.objects.get_or_create(username='testuser')[0])
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 302)

        
class test_main_models(TestCase):
     def setUp(self):
          self.file_mock = mock.MagicMock(spec=File, name='FileMock')
          self.file_mock.name = 'test1.jpg'
          self.user_test = User.objects.get_or_create(username='testuser')[0]
          self.ingrediente_test = IngredienteRicetta.objects.get_or_create(ingrediente='carciofi', quantità='100g')[0]
          self.ricettario_test = ricettario.objects.create(user = self.user_test, name = 'test', immagine = self.file_mock)
          self.ricetta1 = ricetta.objects.create(
               nome = 'test_ricetta',
               prontoin = '10',
               persone = 4,
               immagine = self.file_mock,
               portata = 'testportata',
               procedimento = 'test_procedimento',
               punteggiosalute = 58,
               tipidieta = '[vegana, vegetariana]' 
          )
          self.ricetta1.save()
          self.ricetta1.ingredienti.add(self.ingrediente_test)
          self.recensione = Recensione.objects.create(ricetta = self.ricetta1, punteggio=4)
          

     def test_model_recensione_return(self):
          self.assertEqual(str(self.recensione), 'test_ricetta')

     def test_model_ricettario_return(self):
          self.assertEqual(str(self.ricettario_test), 'test')

     def test_model_ricetta_return(self):
          self.assertEqual(str(self.ricetta1), 'test_ricetta')
     
     def test_model_ingrediente_return(self):
          self.assertEqual(str(self.ingrediente_test), str(self.ingrediente_test.quantità) + " " + str(self.ingrediente_test.ingrediente))
        
class test_main_views(TestCase):
     def setUp(self):
          self.client = Client()
          self.file_mock = mock.MagicMock(spec=File, name='FileMock')
          self.file_mock.name = 'test1.jpg'
          self.user_test = User.objects.get_or_create(username='testuser')[0]
          self.user_test2 = User.objects.get_or_create(username='testuser2')[0]
          self.ricettario_test = ricettario.objects.create(user = self.user_test, name = 'test', immagine = self.file_mock)
          self.home_url = reverse('homepage')
          self.ricettatest = ricetta.objects.create(
               nome = 'test_ricetta',
               prontoin = '10',
               persone = 4,
               immagine = self.file_mock,
               portata = 'testportata',
               procedimento = 'test_procedimento',
               punteggiosalute = 58,
               tipidieta = '[vegana, vegetariana]' 
          )
          self.ricettatest.save()
          self.ricettatest2 = ricetta.objects.create(
               nome = 'test_ricetta2',
               prontoin = '5',
               persone = 2,
               immagine = self.file_mock,
               portata = 'testportata2',
               procedimento = 'test_procedimento2',
               punteggiosalute = 68,
               tipidieta = '[vegana, vegetariana]' 
          )
          self.ricettatest2.save()
          self.ricettatest.ricettario.add(self.ricettario_test)
          self.dict = {'Scampi':'10g'}
          self.valutaric_url = reverse('valuta_ricetta')
          self.aggiungispesa_url = reverse('aggiungispesa')
          self.listaspesa_url = reverse('listaspesa')
          self.puliscispesa_url = reverse('puliscispesa')
          self.scarica_url = reverse('scaricaricette')
          self.spesa = Spesa.objects.create(user = self.user_test)
          self.ingrediente1 = IngredienteRicetta.objects.create(ingrediente = 'Scampi', quantità = '10g')
          self.ingrediente2 = IngredienteRicetta.objects.create(ingrediente = 'Noci', quantità='5g')
          self.spesa.ingredienti.add(self.ingrediente1)
          self.spesa.ingredienti.add(self.ingrediente2)
          

     def test_main_views_puliscispesa(self):
          u = User.objects.get_or_create(username='testuser2')[0]
          self.client.force_login(u)
          s = Spesa.objects.create(user = u)
          response = self.client.get(self.puliscispesa_url)
          self.assertEqual(response.status_code, 302)
     

     def test_main_views_listaspesa(self):
          self.client.force_login(User.objects.get_or_create(username='testuser')[0])
          response = self.client.get(self.listaspesa_url)
          self.assertEqual(response.status_code, 200)
          self.assertTemplateUsed(response, 'main/listaspesa.html')

     def test_main_views_aggiungispesa(self):
          self.client.force_login(User.objects.get_or_create(username='testuser')[0])
          response = self.client.post(self.aggiungispesa_url, {
               'dizionario': json.dumps(self.dict)
          })
          self.assertEqual(response.status_code, 200)

     def test_main_views_valutaric_ex(self):
          self.client.force_login(self.user_test)
          Recensione.objects.create(user = self.user_test, ricetta = self.ricettatest, punteggio = 3)
          response = self.client.post(self.valutaric_url, {
               'r_id': self.ricettatest.id,
               'val': 4
          })
          self.assertEqual(response.status_code, 200)

     def test_main_views_valutaric_notex(self):
          self.client.force_login(self.user_test)
          response = self.client.post(self.valutaric_url, {
               'r_id': self.ricettatest.id,
               'val': 3
          })
          self.assertEqual(response.status_code, 200)

     def test_main_views_valutaric_GET(self):
          self.client.force_login(self.user_test)
          response = self.client.get(self.valutaric_url)
          self.assertEqual(response.status_code, 500)

     # def test_main_views_valutaric_get(self):
     #      response = self.client.get(self.valutaric_url) 
     #      self.assertEqual(response.status_code, 500)

     def test_main_views_esplora(self):
          self.client.force_login(self.user_test)
          response = self.client.get(self.home_url)
          self.assertEqual(response.status_code, 200)
     
     def test_main_views_scaricaricette(self):
          self.client.force_login(self.user_test)
          response = self.client.get(self.scarica_url)
          self.assertEqual(response.status_code, 302)

     def test_main_views_esploraPOSTsalva(self):
          self.client.force_login(self.user_test)
          response = self.client.post(self.home_url, {'action':'Salva', 'ricettari':self.ricettario_test, 'ricetta':self.ricettatest.id})
          self.assertEqual(response.status_code, 302)

     def test_main_views_esploraGET(self):
          self.client.force_login(self.user_test)
          Recensione.objects.create(user = self.user_test, ricetta= self.ricettatest, punteggio = 5)
          Recensione.objects.create(user = self.user_test2, ricetta= self.ricettatest, punteggio = 5)
          Recensione.objects.create(user = self.user_test2, ricetta= self.ricettatest2, punteggio= 4)
          response = self.client.get(self.home_url)
          self.assertEqual(response.status_code, 200)
          self.assertTemplateUsed(response, 'main/esplora.html')

     # def test_main_views_esploraPOSTcerca(self):
     #      self.client.force_login(self.user_test)
     #      response = self.client.post(self.home_url, {'action':'Cerca', 'text_search': 'pollo'})
     #      self.assertEqual(response.status_code, 200)
     #      self.assertTemplateUsed(response, 'main/esplora.html')

class test_ricette_forms(TestCase):
     def setUp(self):
          self.client = Client()
          self.user_test = User.objects.get_or_create(username='testuser')[0]
          self.file_mock = mock.MagicMock(spec=File, name='FileMock')
          self.file_mock.name = 'test1.jpg'
          self.ricettatest = ricetta.objects.create(
               nome = 'test_ricetta',
               prontoin = '10',
               persone = 4,
               immagine = self.file_mock,
               portata = 'testportata',
               procedimento = 'test_procedimento',
               punteggiosalute = 58,
               tipidieta = '[vegana, vegetariana]' 
          )
          self.ricettatest.save()
          self.ingrediente = IngredienteRicetta.objects.create(quantità = '10g', ingrediente = 'tonno')
          self.ricettatest.ingredienti.add(self.ingrediente)

     def test_formricetta(self):
          self.client.force_login(self.user_test)
          form = FormRicetta(ingredienti = 1, utente = self.user_test, data = {
               'nome_ricetta' : 'test',
               'procedimento_ricetta': 'test',
               'immagine_ricetta': self.file_mock,
               'prontoin': 5,
               'persone': 4,
               'portata': 'antipasto',
               'punteggiosalute': 4,
               'tipidieta': 'vegana',
          })
          self.assertFalse(form.is_valid())

     def test_forming(self):
          self.client.force_login(self.user_test)
          form = FormCheckIngr(r = self.ricettatest, data = {})
          
          self.assertFalse(form.is_valid())
          
class test_ricette_views(TestCase):
     def setUp(self):
          self.client = Client()
          self.campi = 1
          self.file_mock = mock.MagicMock(spec=File, name='FileMock')
          self.file_mock.name = 'test1.jpg'
          self.user_test = User.objects.get_or_create(username='testuser')[0]
          self.ricettario_test = ricettario.objects.create(user = self.user_test, name = 'test', immagine = self.file_mock)
          self.ricetta_test = ricetta.objects.create(nome = 'test', prontoin = '10 m', persone = 3, immagine = self.file_mock, portata = 'primo', procedimento = 'test', punteggiosalute = 10, tipidieta = 'vegana')
          self.ingrediente = IngredienteRicetta.objects.create(quantità = '10g', ingrediente = 'tonno')
          self.ricetta_test.ingredienti.add(self.ingrediente)
          with reversion.create_revision():
               self.ricetta_test.save()
          self.ricetta_test.ricettario.add(self.ricettario_test)
          self.visualricetta_url = reverse('visual_ricetta', kwargs={'id': self.ricetta_test.id})
          self.eliminaricetta_url = reverse('elimina_ricetta', kwargs={'id': self.ricetta_test.id})
          self.ricette_url = reverse('ricette', kwargs={'campi': self.campi})
          self.campi_url = reverse('numerocampi')
          self.ricettario_url = reverse('crearic')
          self.gestione_url = reverse('gestioneric')
          self.proponimodifica_url = reverse('proponimodifica', kwargs={'id': self.ricetta_test.id})
          self.vecchiaversione_url = reverse('vecchiaversione', kwargs={'id': self.ricetta_test.id})
          self.visualricettario_url = reverse('ricettario', kwargs={'idricettario': self.ricettario_test.id})
          self.eliminaric_url = reverse('eliminaric', kwargs={'id': self.ricettario_test.id})

     def test_ricette_views_numcampi(self):
          self.client.force_login(self.user_test)
          response = self.client.post(self.campi_url, {'campi': self.campi})
          self.assertEqual(response.status_code, 302)

     def test_ricette_views_numcampi_else(self):
          self.client.force_login(self.user_test)
          response = self.client.get(self.campi_url)
          self.assertEqual(response.status_code, 200)
          self.assertTemplateUsed(response, 'numerocampi.html')

     def test_ricette_views_ricette_autPOST(self):
          self.client.force_login(self.user_test)
          response = self.client.post(self.ricette_url, {
               'nome_ricetta':'rictest',
               'procedimento_ricetta':'desctest',
               'immagine_ricetta': self.file_mock,
               'ricettari': self.ricettario_test.name,
               'prontoin': 4,
               'persone': 3,
               'portata': 'antipasto',
               'punteggiosalute': 5,
               'tipidieta': 'vegana',
               'quantità1': '10g',
               'ingrediente1': 'tonno',
          })
          self.assertEqual(response.status_code, 302)
        
     def test_ricette_views_ricette_autGET(self):
          self.client.force_login(User.objects.get_or_create(username='testuser')[0])
          response = self.client.get(self.ricette_url)
          self.assertEqual(response.status_code, 200)
          self.assertTemplateUsed(response, 'crea_ricetta.html')

     def test_ricette_views_ricette_notaut(self):
          response = self.client.get(self.ricette_url)
          self.assertEqual(response.status_code, 302)
    
     def test_ricette_views_eliminaricetta_aut(self):
          self.client.force_login(self.user_test)
          response = self.client.get(self.eliminaricetta_url)
          self.assertEqual(response.status_code, 302)
        
     def test_ricette_views_visualricetta_aut(self):
          self.client.force_login(self.user_test)
          recensione_test = Recensione(user = self.user_test, ricetta = self.ricetta_test, punteggio = 2)
          recensione_test.save()
          response = self.client.get(self.visualricetta_url)
          self.assertEqual(response.status_code, 200)
          self.assertTemplateUsed(response, 'visual_ricetta.html')

     def test_ricette_views_visualricetta_aut_norecensione(self):
          self.client.force_login(self.user_test)
          response = self.client.get(self.visualricetta_url)
          self.assertEqual(response.status_code, 200)
          self.assertTemplateUsed(response, 'visual_ricetta.html')
          
     def test_ricette_views_crearicettario_post(self):
          self.client.force_login(self.user_test)
          response = self.client.post(self.ricettario_url, {
               'name':'test',
               'immagine': self.file_mock
          })
          self.assertEqual(response.status_code, 302)

     def test_ricette_views_crearicettario_get(self):
          self.client.force_login(self.user_test)
          response = self.client.get(self.ricettario_url)
          self.assertEqual(response.status_code, 200)
          self.assertTemplateUsed(response, 'crea_ricettario.html')

     def test_ricette_views_gestioneric(self):
          self.client.force_login(self.user_test)
          response = self.client.get(self.gestione_url)
          self.assertEqual(response.status_code, 200)
          self.assertTemplateUsed(response, 'gestione_ricettari.html')

     def test_ricette_views_visualricettario(self):
          self.client.force_login(self.user_test)
          response = self.client.get(self.visualricettario_url)
          self.assertEqual(response.status_code, 200)
          self.assertTemplateUsed(response, 'visual_ricettario.html')
     
     def test_ricette_views_eliminaric(self):
          self.client.force_login(self.user_test)
          response = self.client.get(self.eliminaric_url)
          self.assertEqual(response.status_code, 302)

     def test_ricette_views_proponimodifica_aggingr(self):
          self.client.force_login(self.user_test)
          response = self.client.post(self.proponimodifica_url, {
               'action' : 'aggingr',
               'quantità': '10g',
               'ingrediente':'tonno'
          })
          self.assertEqual(response.status_code, 302)

     def test_ricette_views_proponimodifica_eliminaingr(self):
          self.client.force_login(self.user_test)
          self.ricetta_test.ingredienti.add(IngredienteRicetta.objects.create(quantità = '10g', ingrediente = 'tonno'))
          self.ricetta_test.ingredienti.add(IngredienteRicetta.objects.create(quantità = '20g', ingrediente = 'salame'))
          lista = []
          for element in self.ricetta_test.ingredienti.all():
               lista.append(element.id)
          response = self.client.post(self.proponimodifica_url, {
               'action' : 'eliminaingr',
               'ingredienti' : lista
          })
          self.assertEqual(response.status_code, 302)

     def test_ricette_views_proponimodifica_salva(self):
          self.client.force_login(self.user_test)
          response = self.client.post(self.proponimodifica_url, {
               'action' : 'salvamodifiche',
               'nome': 'test',
               'portata': 'test',
               'procedimento': 'test',
               'punteggiosalute': 20,
               'tipidieta': 'vegana',    
               })
          self.assertEqual(response.status_code, 302)

     def test_ricette_views_proponimoficaget(self):
          self.client.force_login(self.user_test)
          response = self.client.get(self.proponimodifica_url)
          self.assertEqual(response.status_code, 200)
          self.assertTemplateUsed(response, 'proponimodifica.html')

     def test_ricette_views_vecchiaversione(self):
          self.client.force_login(self.user_test)
          response = self.client.get(self.vecchiaversione_url)
          self.assertEqual(response.status_code, 200)
          self.assertTemplateUsed(response, 'vecchiaversione.html')
          
class test_chat_views(TestCase):
     def setUp(self):
          self.client = Client()
          self.user_test = User.objects.get_or_create(username='testuser')[0]
          self.newgroup_url = reverse('new_group')
          self.chat_url = reverse('chat')
          self.group_test = Group.objects.create(uuid='10bbf91a-6dd9-4f9f-a5dd-d7a9c7a71593')
          self.uuid_test = '10bbf91a-6dd9-4f9f-a5dd-d7a9c7a71593'
          self.joingroup_url = reverse('join_group', kwargs={'uuid': self.uuid_test})
          self.leavegroup_url = reverse('leave_group', kwargs={'uuid': self.uuid_test})
          self.openchat_url = reverse('open_chat', kwargs={'uuid': self.uuid_test})
          self.removegroup_url = reverse('remove_group', kwargs={'uuid': self.uuid_test})

     def test_chat_views_chat(self):
          self.client.force_login(self.user_test)
          response = self.client.get(self.chat_url)
          self.assertEqual(response.status_code, 200)
          self.assertTemplateUsed(response, 'chat.html')

     def test_chat_views_newgroup(self):
          self.client.force_login(self.user_test)
          response = self.client.get(self.newgroup_url)
          self.assertEqual(response.status_code, 302)

     def test_chat_views_joingroup(self):
          self.client.force_login(self.user_test)
          response = self.client.get(self.joingroup_url)
          self.assertEqual(response.status_code, 302)

     def test_chat_views_leavegroup(self):
          self.client.force_login(self.user_test)
          response = self.client.get(self.leavegroup_url)
          self.assertEqual(response.status_code, 302)
     
     def test_chat_views_openchat_userin(self):
          self.client.force_login(self.user_test)
          self.group_test.members.add(self.user_test)
          response = self.client.get(self.openchat_url)
          self.assertEqual(response.status_code, 200)
          self.assertTemplateUsed(response, 'chat_open.html')

     def test_chat_views_openchat_usernotin(self):
          self.client.force_login(self.user_test)
          response = self.client.get(self.openchat_url)
          self.assertEqual(response.status_code, 403)


     def test_chat_views_removegroup(self):
          self.client.force_login(self.user_test)
          response = self.client.get(self.removegroup_url)
          self.assertEqual(response.status_code, 302)

class test_chat_models(TestCase):
     def setUp(self):
          self.client = Client()
          self.user_test = User.objects.get_or_create(username='testuser')[0]
          self.user_test2 = User.objects.get_or_create(username='testuser2')[0]
          self.group_test = Group.objects.create(uuid='10bbf91a-6dd9-4f9f-a5dd-d7a9c7a71593')
          self.group_test.members.add(self.user_test2)
     
     def test_chat_model_groupadduser(self):
          request = self.group_test.add_user(self.user_test)
          self.assertEqual(request, True)
          
     def test_chat_model_groupremoveuser(self):
          request = self.group_test.remove_user(self.user_test2)
          self.assertEqual(request, True)


