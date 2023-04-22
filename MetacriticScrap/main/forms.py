#encoding:utf-8
import datetime
from django import forms
from django.forms import NumberInput
from main.models import Genero, Consola, Desarrolladora, Clasificacion, Juego
from pymongo import MongoClient
from decouple import config

client = MongoClient(config('BD_HOST'))
db = client[config('BD_NAME')]
juegos = db.main_juego
consolas = db.main_consola
generos = db.main_genero
desarrolladoras = db.main_desarrolladora
clasificaciones = db.main_clasificacion
juego_desarrolladoras = db.main_juego_desarrolladoras
juego_generos = db.main_juego_generos
juego_otrasConsolas = db.juego_otrasConsolas

class BuscarNombreForm(forms.Form):
    nombre = forms.CharField(label='Nombre', max_length=100)

class BuscarDescripcionForm(forms.Form):
    descripcion = forms.CharField(label='Descripción', max_length=100)

class BuscarRankingForm(forms.Form):
    numeroJuegos = db.main_juego.count_documents({})
    ranking = forms.IntegerField(label='Ranking', max_value=numeroJuegos, min_value=1)

class BuscarRankingComparadorForm(forms.Form):
    numeroJuegos = db.main_juego.count_documents({})
    rankingComparador = forms.IntegerField(label='Ranking', max_value=numeroJuegos, min_value=1)

class BuscarPuntMetaForm(forms.Form):
    puntMeta = forms.IntegerField(label='Puntuación Metacritic', max_value=100, min_value=0)

class BuscarPuntUsuForm(forms.Form):
    puntUsu = forms.FloatField(label='Puntuación Usuarios', max_value=10, min_value=0, widget=NumberInput(attrs={'step': "0.1"}))

class BuscarGeneroForm(forms.Form):
    generos = db.main_genero.find().sort('nombre')
    opciones_generos = [(genero['nombre'], genero['nombre']) for genero in generos]
    genero = forms.ChoiceField(choices=opciones_generos)

class BuscarConsolaForm(forms.Form):
    consolas = db.main_consola.find().sort('nombre')
    opciones_consolas = [(consola['nombre'], consola['nombre']) for consola in consolas]
    consola = forms.ChoiceField(choices=opciones_consolas)

class BuscarDesarrolladoraForm(forms.Form):
    desarrolladoras = db.main_desarrolladora.find().sort('nombre')
    opciones_desarrolladoras = [(desarrolladora['nombre'], desarrolladora['nombre']) for desarrolladora in desarrolladoras]
    desarrolladora = forms.ChoiceField(choices=opciones_desarrolladoras)

class BuscarClasificacionForm(forms.Form):
    clasificaciones = db.main_clasificacion.find().sort('nombre')
    opciones_clasificaciones = [(clasificacion['nombre'], clasificacion['nombre']) for clasificacion in clasificaciones]
    clasificacion = forms.ChoiceField(choices=opciones_clasificaciones)

class BuscarFechaLanzamientoForm(forms.Form):
    anyoActual = datetime.datetime.now().year
    fechaLanzamiento = forms.IntegerField(label='Año de lanzamiento', max_value=anyoActual, min_value=1900)