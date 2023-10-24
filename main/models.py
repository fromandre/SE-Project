from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
import reversion

# Create your models here.
# Modelli del Database

class ricettario(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="ricettario", null=True)
    name = models.CharField(max_length=100)
    immagine = models.ImageField(upload_to="img")
    def __str__(self):
        return self.name

class IngredienteRicetta(models.Model):
    ingrediente = models.CharField(max_length=100, blank=True, null=True)
    quantità = models.CharField(max_length=100, blank=True, null=True)
    def __str__(self):
        return str(self.quantità) + " " + str(self.ingrediente)

@reversion.register
class ricetta(models.Model):
    ricettario = models.ManyToManyField(ricettario)
    nome = models.CharField(max_length=100)
    prontoin = models.CharField(max_length=100)
    persone = models.IntegerField()
    immagine = models.ImageField(upload_to="img")
    ingredienti = models.ManyToManyField(IngredienteRicetta)
    portata = models.CharField(max_length=50)
    procedimento = models.CharField(max_length=2000)
    punteggiosalute = models.IntegerField()
    tipidieta = models.CharField(max_length=100)
    class Versioning:
        ultimamodifica = 'date'
        clear = ['log']
    def __str__ (self):
        return self.nome

class Recensione(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="recensione", null=True)
    ricetta = models.ForeignKey(ricetta, on_delete=models.CASCADE, related_name="ricetta", null=True)
    punteggio = models.IntegerField(default=0,
        validators = [
            MaxValueValidator(5),
            MinValueValidator(0)
        ]
    )
    def __str__(self):
        return str(self.ricetta)
    
class Spesa(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="spesa", null=True) 
    ingredienti = models.ManyToManyField(IngredienteRicetta)
    

