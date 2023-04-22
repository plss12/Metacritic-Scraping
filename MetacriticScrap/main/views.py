from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from main.models import Genero, Consola, Desarrolladora, Clasificacion, Juego
from main.populate import populate_database, populate_whoosh
from whoosh.index import open_dir
from whoosh.qparser import QueryParser
from django.core.paginator import Paginator
from django.http.response import HttpResponseRedirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.conf import settings
from decouple import config
from pymongo import MongoClient

client = MongoClient(config('BD_HOST'))
db = client[config('BD_NAME')]
juegos = db.main_juego
numeroJuegos = juegos.count_documents({})

def index (request):

    return render(request, 'index.html',{'numero': numeroJuegos})

