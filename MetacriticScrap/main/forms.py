#encoding:utf-8
import datetime
from django import forms
from django.forms import NumberInput
from main.models import Genero, Consola, Desarrolladora, Clasificacion, Juego

class BuscarNombreForm(forms.Form):
    nombre = forms.CharField(label='Nombre', max_length=100)

class BuscarDescripcionForm(forms.Form):
    descripcion = forms.CharField(label='Descripción', max_length=100)

class BuscarRankingForm(forms.Form):
    numeroJuegos = Juego.objects.all().count()
    ranking = forms.IntegerField(label='Ranking', max_value=numeroJuegos, min_value=1)

class BuscarRankingComparadorForm(forms.Form):
    numeroJuegos = Juego.objects.all().count()
    rankingComparador = forms.IntegerField(label='Ranking', max_value=numeroJuegos, min_value=1)

class BuscarPuntMetaForm(forms.Form):
    puntMeta = forms.IntegerField(label='Puntuación Metacritic', max_value=100, min_value=0)

class BuscarPuntUsuForm(forms.Form):
    puntUsu = forms.FloatField(label='Puntuación Usuarios', max_value=10, min_value=0, widget=NumberInput(attrs={'step': "0.1"}))

class BuscarGeneroForm(forms.Form):
    generos = Genero.objects.all().order_by('nombre')
    genero = forms.ModelChoiceField(queryset=generos)

class BuscarConsolaForm(forms.Form):
    consolas = Consola.objects.all().order_by('nombre')
    consola = forms.ModelChoiceField(queryset=consolas)

class BuscarDesarrolladoraForm(forms.Form):
    desarrolladoras = Desarrolladora.objects.all().order_by('nombre')
    desarrolladora = forms.ModelChoiceField(queryset=desarrolladoras)

class BuscarClasificacionForm(forms.Form):
    clasificaciones = Clasificacion.objects.all().order_by('nombre')
    clasificacion = forms.ModelChoiceField(queryset=clasificaciones)

class BuscarFechaLanzamientoForm(forms.Form):
    anyoActual = datetime.datetime.now().year
    fechaLanzamiento = forms.IntegerField(label='Año de lanzamiento', max_value=anyoActual, min_value=1900)