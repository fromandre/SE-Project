import os, sys
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mynowandthen.settings')
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
from main.models import Item, ricetta, ricettario, IngredienteRicetta, Recensione, Spesa
from chat.models import Group, Message
import requests


# Create your tests here.
class test_autenticazione_views_post(TestCase):
    def setUp(self):
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.utente = {'email':'usertest@gmail.com', 'username':'usertest', 'password':'testpassword123'}
        self.client = Client()

    def test_registerview_nuovo(self):
          response = self.client.post(self.register_url, self.utente)
          # form = RegisterForm(data=self.utente)
          # if form.is_valid():
          #      form.save()
          self.assertEqual(response.status_code, 302)

    def test_registerview_else(self):
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
               ricettario = self.ricettario_test,
               ricetta_nome= 'test_ricetta',
               ricetta_descrizione = 'test_descr',
               ricetta_immagine = self.file_mock,
          )
          self.ricetta1.ricetta_ingredienti.add(self.ingrediente_test)
          self.recensione = Recensione.objects.create(ricetta = self.ricetta1, punteggio=4)
          self.item1 = Item.objects.create(ricetta = self.ricetta1)

     def test_model_recensione_return(self):
          self.assertEqual(str(self.recensione), '4')

     def test_model_ricettario_return(self):
          self.assertEqual(str(self.ricettario_test), 'test')

     def test_model_ricetta_return(self):
          self.assertEqual(str(self.ricetta1), 'test_ricetta')
        
     def test_model_item_return(self):
          self.assertEqual(str(self.item1), 'test_ricetta')
        
class test_main_views(TestCase):
     def setUp(self):
          self.client = Client()
          self.file_mock = mock.MagicMock(spec=File, name='FileMock')
          self.file_mock.name = 'test1.jpg'
          self.user_test = User.objects.get_or_create(username='testuser')[0]
          self.ricettario_test = ricettario.objects.create(user = self.user_test, name = 'test', immagine = self.file_mock)
          self.home_url = reverse('homepage')
          self.ricetta_test = requests.get("http://www.themealdb.com/api/json/v1/1/lookup.php?i=53064").json()
          self.ricetta_test2 = ricetta.objects.create(ricettario = self.ricettario_test, ricetta_nome='testnome', ricetta_descrizione='testdesc', ricetta_immagine=self.file_mock)
          self.dict = {'Scampi':'10g'}
          self.cat = 'Seafood'
          self.esploracat_url = reverse('esploracat', kwargs={'cat': self.cat})
          self.apriric_url = reverse('apriric', kwargs={'id': 53064})
          self.valutaric_url = reverse('valuta_ricetta')
          self.aggiungispesa_url = reverse('aggiungispesa')
          self.listaspesa_url = reverse('listaspesa')
          self.puliscispesa_url = reverse('puliscispesa')
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
          r = Recensione.objects.create(ricetta = self.ricetta_test2, punteggio=4)
          r.save()
          response = self.client.post(self.valutaric_url, {
               'r_id': self.ricetta_test2.id,
               'val': 3
          })
          self.assertEqual(response.status_code, 200)
     
     def test_main_views_valutaric_notex(self):
          response = self.client.post(self.valutaric_url, {
               'r_id': self.ricetta_test2.id,
               'val': 3
          })
          self.assertEqual(response.status_code, 200)

     def test_main_views_valutaric_get(self):
          response = self.client.get(self.valutaric_url) 
          self.assertEqual(response.status_code, 500)

     def test_main_views_apriric_post(self):
          response = self.client.post(self.apriric_url, {
               'ricettari': self.ricettario_test.name
          })
          self.assertEqual(response.status_code, 302)
  

     def test_main_views_apriric_else(self):
          response = self.client.get(self.apriric_url)
          self.assertEqual(response.status_code,200)
          self.assertTemplateUsed(response, 'analizza_ricetta.html')

     def test_main_views_esploracat(self):
          response = self.client.get(self.esploracat_url)
          self.assertEqual(response.status_code, 200)
          self.assertTemplateUsed(response, 'main/esplora_ricette.html')

     def test_main_views_estraingr(self):
          self.assertEqual(type(m.estrai_ingr(self.ricetta_test)), type(self.dict))


     def test_main_views_esplora_aut_post(self):
          self.client.force_login(User.objects.get_or_create(username='testuser')[0])
          response = self.client.post(self.home_url, {'text_search':'test'})
          self.assertEqual(response.status_code, 200)
          self.assertTemplateUsed(response, 'main/esplora_ricette.html')
     
     def test_main_views_esplora_aut_get(self):
          self.client.force_login(User.objects.get_or_create(username='testuser')[0])
          response = self.client.get(self.home_url)
          self.assertEqual(response.status_code, 200)
          self.assertTemplateUsed(response, 'main/esplora.html')
        
     def test_main_views_esplora_not_aut(self):
          response = self.client.get(self.home_url)
          self.assertEqual(response.status_code, 302)

class test_ricette_views(TestCase):
     def setUp(self):
          self.client = Client()
          self.campi = 1
          self.file_mock = mock.MagicMock(spec=File, name='FileMock')
          self.file_mock.name = 'test1.jpg'
          self.user_test = User.objects.get_or_create(username='testuser')[0]
          self.ricettario_test = ricettario.objects.create(user = self.user_test, name = 'test', immagine = self.file_mock)
          self.ricetta_test = ricetta.objects.create(ricettario = self.ricettario_test, ricetta_nome='testnome', ricetta_descrizione='testdesc', ricetta_immagine=self.file_mock)
          self.ricetta_test.save()
          self.visualricetta_url = reverse('visual_ricetta', kwargs={'id': self.ricetta_test.id})
          self.eliminaricetta_url = reverse('elimina_ricetta', kwargs={'id': self.ricetta_test.id})
          self.ricette_url = reverse('ricette', kwargs={'campi': self.campi})
          self.campi_url = reverse('numerocampi')
          self.ricettario_url = reverse('crearic')
          self.gestione_url = reverse('gestioneric')
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
               'ricettari': self.ricettario_test,
               'quantità1': '100g',
               'ingrediente1' : 'carciofi',
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
          recensione_test = Recensione(ricetta = self.ricetta_test, punteggio = 2)
          recensione_test.save()
          self.client.force_login(self.user_test)
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


