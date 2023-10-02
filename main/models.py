from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator


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

class ricetta(models.Model):
    ricettario = models.ForeignKey(ricettario, on_delete=models.CASCADE, related_name="ricetta", null=True)
    ricetta_nome = models.CharField(max_length=100)
    ricetta_descrizione = models.TextField()
    ricetta_immagine = models.ImageField(upload_to="img")
    ricetta_ingredienti = models.ManyToManyField(IngredienteRicetta)
    def __str__ (self):
        return self.ricetta_nome

class Recensione(models.Model):
    ricetta = models.ForeignKey(ricetta, on_delete=models.CASCADE, related_name="ricetta", null=True)
    punteggio = models.IntegerField(default=0,
        validators = [
            MaxValueValidator(5),
            MinValueValidator(0)
        ]
    )
    def __str__(self):
        return str(self.punteggio)
    
class Spesa(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="spesa", null=True) 
    ingredienti = models.ManyToManyField(IngredienteRicetta)
    
class Item(models.Model): 
    ricetta = models.ForeignKey(ricetta, on_delete=models.CASCADE)
    def __str__(self):
        return self.ricetta.ricetta_nome
