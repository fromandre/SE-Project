from django.contrib import admin
from . import models
# Register your models here.
#comando per aggiungere modelli alla dashboard_admin

admin.site.register(models.ricetta)
admin.site.register(models.Item)
admin.site.register(models.ricettario)
admin.site.register(models.IngredienteRicetta)
admin.site.register(models.Recensione)
admin.site.register(models.Spesa)