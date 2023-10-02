from django.urls import path
from . import views
from ricette.views import * 

#Pattern da seguire nell'url

urlpatterns = [
    path("", views.register, name="auth"),
    path("homepage", views.esplora, name="homepage"),
    path("numerocampi", numerocampi, name="numerocampi"),
    path("ricette/<campi>", ricette, name="ricette"),
    path("crearic", crea_ricettario, name="crearic"),
    path("ricettario/<idricettario>", visual_ricettario, name="ricettario"),
    path("eliminaric/<id>", elimina_ricettario, name="eliminaric"),
    path("gestioneric", gestione_ricettari, name="gestioneric"),
    path("elimina_ricetta/<id>", elimina_ricetta, name="elimina_ricetta"),
    path("visual_ricetta/<id>", visual_ricetta, name="visual_ricetta"),
    path("valuta_ricetta/", views.valuta_ricetta, name="valuta_ricetta"),
    path("esploracat/<cat>", views.esplora_cat, name="esploracat"),
    path("apriric/<id>", views.apri_ric, name="apriric"),
    path("aggiungispesa/", views.aggiungispesa, name="aggiungispesa"),
    path("listaspesa/", views.listaspesa, name="listaspesa"),
    path("puliscispesa/", views.puliscispesa, name="puliscispesa"),
]


