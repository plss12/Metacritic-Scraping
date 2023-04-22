from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from main.populate import populate_database, populate_whoosh
from main.forms import *
from whoosh.index import open_dir
from whoosh.qparser import QueryParser
from django.core.paginator import Paginator
from django.http.response import HttpResponseRedirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.conf import settings
from pymongo import MongoClient
from pymongo import DESCENDING
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

def index (request):
    return render(request, 'index.html')

def todosJuegos(request,number=1):
    number = int(number)
    juegos = list(db.main_juego.find().sort("ranking"))
    todosJuegos_total = Paginator(juegos,10)
    if number > todosJuegos_total.num_pages:
        number = todosJuegos_total.num_pages
    juegos = todosJuegos_total.get_page(number)
    num_pages = todosJuegos_total.num_pages
    previus = number - 1
    next = number + 1
    if(number>=4):
        if(number>=num_pages-3):
            rango = range(number-3,num_pages+1)
        else:
            rango = range(number-3,number+4)
    elif(number<4):
        rango = range(1, number+4)

    if(next>num_pages):
        return render(request, 'todosJuegos.html', {'todosJuegos': juegos, 'num_pages': num_pages, 'number': number, 'previus': previus, 'range': rango})
    elif(previus<1):
        return render(request, 'todosJuegos.html', {'todosJuegos': juegos, 'num_pages': num_pages, 'number': number, 'next': next, 'range': rango})
    else:
        return render(request, 'todosJuegos.html', {'todosJuegos': juegos, 'num_pages': num_pages, 'number': number, 'previus': previus, 'next': next, 'range': rango})

def juegosRecientes(request):
    juegosRecientes = list(db.main_juego.find().sort("fechaLanzamiento", -1).limit(25))
    mensaje="Juegos Más Recientes"
    return render(request, 'listaJuegos.html', {'juegos': juegosRecientes, 'mensaje': mensaje})

def mejoresJuegos(request):
    mejoresJuegos = list(db.main_juego.find().sort("ranking").limit(100))
    mensaje="Top 100 Mejores Juegos segun Metacritic"
    return render(request, 'listaJuegos.html', {'juegos': mejoresJuegos, 'mensaje': mensaje})

def mejoresJuegosUsu(request):
    mejoresJuegosUsu = list(db.main_juego.find().sort("puntuacionUsuarios",DESCENDING).limit(100))
    mensaje="Top 100 Mejores Juegos segun los usuarios"
    return render(request, 'listaJuegos.html', {'juegos': mejoresJuegosUsu, 'mensaje': mensaje})

def listaConsolas(request):
    consolas = list(db.main_consola.find().sort("nombre"))
    return render(request, 'listas.html', {'objetos': consolas, 'tipo': 'Consolas'})

def consolaFiltro(request, consola):
    if(' --- ' in consola):
        consola = consola.replace(' --- ', '/')
    consola = db.main_consola.find_one({'nombre': consola})
    juegos = list(db.main_juego.find({'consola_id': consola['nombre']}))
    if(len(juegos) == 0):
        return render(request, 'filtroListas.html', {'tipo': 'Consolas', 'juegos': juegos, 'filtro': consola['nombre'], 'error': 'No hay ningún juego que sea principalmente para esta consola'})
    return render(request, 'filtroListas.html', {'tipo': 'Consolas', 'juegos': juegos, 'filtro': consola['nombre']})

def listaDesarrolladoras(request):
    desarrolladoras = list(db.main_desarrolladora.find().sort("nombre"))
    return render(request, 'listas.html', {'objetos': desarrolladoras, 'tipo': 'Desarrolladoras'})

def desarrolladoraFiltro(request, desarrolladora):
    if(' --- ' in desarrolladora):
        desarrolladora = desarrolladora.replace(' --- ', '/')

    desarrolladora = db.main_desarrolladora.find_one({'nombre': desarrolladora})
    juegosIDs = db.main_juego_desarrolladoras.distinct('juego_id', {'desarrolladora_id': desarrolladora["nombre"]})
    juegos = list(db.main_juego.find({'ranking': {'$in': juegosIDs}}))

    return render(request, 'filtroListas.html', {'tipo': 'Desarrolladoras', 'juegos': juegos, 'filtro': desarrolladora["nombre"]})

def listaGeneros(request):
    generos = list(db.main_genero.find().sort("nombre"))
    return render(request, 'listas.html', {'objetos': generos, 'tipo': 'Generos'})

def generoFiltro(request, genero):
    if(' --- ' in genero):
        genero = genero.replace(' --- ', '/')
    genero = db.main_genero.find_one({'nombre': genero})
    juegosIDs = db.main_juego_generos.distinct('juego_id', {'genero_id': genero["nombre"]})
    juegos = list(db.main_juego.find({'ranking': {'$in': juegosIDs}}))
    return render(request, 'filtroListas.html', {'tipo': 'Generos', 'juegos': juegos, 'filtro': genero["nombre"]})

def listaClasificaciones(request):
    clasificaciones = list(db.main_clasificacion.find().sort("nombre"))
    return render(request, 'listas.html', {'objetos': clasificaciones, 'tipo': 'Clasificaciones'})

def clasificacionFiltro(request, clasificacion):
    if(' --- ' in clasificacion):
        clasificacion = clasificacion.replace(' --- ', '/')
    clasificacion = db.main_clasificacion.find_one({'nombre': clasificacion})
    juegos = list(db.main_juego.find({'clasificacion_id': clasificacion['nombre']}))
    return render(request, 'filtroListas.html', {'tipo': 'Clasificaciones', 'juegos': juegos, 'filtro': clasificacion["nombre"]})

@login_required(login_url='/ingresar')
def populateDB(request):
    if request.method=='POST':
        if 'Aceptar' in request.POST:
            juegos, generos, desarrolladoras, consolas, clasificaciones = populate_database()  
            mensaje="Se han almacenado " + str(juegos) + " juegos, " + str(generos) + " generos, " + str(desarrolladoras) + " desarrolladoras, " + str(consolas) + " consolas y " + str(clasificaciones) + " clasificaciones."
            return render(request, 'cargaCompleta.html', {'mensaje':mensaje, 'tipo': 'BD'})
        else:
            return redirect("/")  
    return render(request, 'confirmacionCarga.html', {'tipo': 'BD'})

@login_required(login_url='/ingresar')
def populateWhoosh(request):
    if request.method=='POST':
        if 'Aceptar' in request.POST:
            num = populate_whoosh()
            mensaje="Se han indexado "+str(num)+" juegos en Whoosh"
            return render(request, 'cargaCompleta.html', {'mensaje':mensaje, 'tipo': 'Whoosh'})
        else:
            return redirect("/")
    return render(request, 'confirmacionCarga.html', {'tipo': 'Whoosh'})

def pagina_juego(request, id):
    juego = db.main_juego.find_one({'ranking': id})
    desarrolladoras = list(db.main_juego_desarrolladoras.find({'juego_id': juego['ranking']}))
    generos = list(db.main_juego_generos.find({'juego_id': juego['ranking']}))
    otrasConsolas = list(db.main_juego_otrasConsolas.distinct('consola_id', {'juego_id': juego['ranking']}))
    if(len(otrasConsolas) == 0):
        return render(request, 'juego.html', {'juego': juego, 'desarrolladoras': desarrolladoras, 'generos': generos})
    else:
        return render(request, 'juego.html', {'juego': juego, 'desarrolladoras': desarrolladoras, 'generos': generos, 'otrasConsolas': otrasConsolas})
    
def buscarNombre(request):
    form = BuscarNombreForm()
    juegos = []
    nombre = ""
    if request.method == 'POST':
        form = BuscarNombreForm(request.POST)
        if form.is_valid():
            nombre = form.cleaned_data['nombre']
    
            directorio = 'Index'
            ix = open_dir(directorio)
            with ix.searcher() as searcher:
                query = QueryParser("nombre", schema=ix.schema).parse(str(nombre))
                results = searcher.search(query, limit=None)
                for r in results:
                    juegos.append(db.main_juego.find_one({'ranking': int(r['id'])}))
    else:
        form = BuscarNombreForm()
    return render(request, 'filtrado.html', {'form': form, 'juegos': juegos, 'filtro': "Nombre", 'filtro2': nombre})

def buscarDescripcion(request):
    form = BuscarDescripcionForm()
    juegos = []
    descripcion = ""
    if request.method == 'POST':
        form = BuscarDescripcionForm(request.POST)
        if form.is_valid():
            descripcion = form.cleaned_data['descripcion']
    
            directorio = 'Index'
            ix = open_dir(directorio)
            with ix.searcher() as searcher:
                query = QueryParser("descripcion", ix.schema).parse(str(descripcion))
                results = searcher.search(query)
                for r in results:
                    juegos.append(db.main_juego.find_one({'ranking': int(r['id'])}))
    else:
        form = BuscarDescripcionForm()
    return render(request, 'filtrado.html', {'form': form, 'juegos': juegos, 'filtro': "Descripción", 'filtro2': descripcion})

def buscarRanking(request):
    form = BuscarRankingForm()
    juegos = []
    ranking = ""
    if request.method == 'POST':
        form = BuscarRankingForm(request.POST)
        if form.is_valid():
            ranking = form.cleaned_data['ranking']
            juegos = db.main_juego.find({'ranking': ranking})
    else:
        form = BuscarRankingForm()
    return render(request, 'filtrado.html', {'form': form, 'juegos': juegos, 'filtro': "Ranking", 'filtro2': ranking})

def filtrarPuntMeta(request):
    form = BuscarPuntMetaForm()
    juegos = []
    puntMeta = ""
    if request.method == 'POST':
        form = BuscarPuntMetaForm(request.POST)
        if form.is_valid():
            puntMeta = form.cleaned_data['puntMeta']
            juegos = db.main_juego.find({'puntuacionMeta': puntMeta})
    else:
        form = BuscarPuntMetaForm()
    return render(request, 'filtrado.html', {'form': form, 'juegos': juegos, 'filtro': "Puntuación Metacritic", 'filtro2': puntMeta})

def filtrarPuntUsu(request):
    form = BuscarPuntUsuForm()
    juegos = []
    puntUsu = ""
    if request.method == 'POST':
        form = BuscarPuntUsuForm(request.POST)
        if form.is_valid():
            puntUsu = form.cleaned_data['puntUsu']
            juegos = list(db.main_juego.find({'puntuacionUsuarios': puntUsu}))
    else:
        form = BuscarPuntUsuForm()
    return render(request, 'filtrado.html', {'form': form, 'juegos': juegos, 'filtro': "Puntuación Usuario", 'filtro2': puntUsu})

def filtrarGenero(request):
    form = BuscarGeneroForm()
    juegos = []
    genero = ""
    if request.method == 'POST':
        form = BuscarGeneroForm(request.POST)
        if form.is_valid():
            genero = form.cleaned_data['genero']
            genero_juegos = list(db.main_juego_generos.find({'genero_id': genero}))
            juego_ids = [juego['juego_id'] for juego in genero_juegos]
            juegos = list(db.main_juego.find({'ranking': {'$in': juego_ids}}))
    else:
        form = BuscarGeneroForm()
    return render(request, 'filtrado.html', {'form': form, 'juegos': juegos, 'filtro': "Género", 'filtro2': genero})

def filtrarConsola(request):
    form = BuscarConsolaForm()
    juegos = []
    consola = ""
    if request.method == 'POST':
        form = BuscarConsolaForm(request.POST)
        if form.is_valid():
            consola = form.cleaned_data['consola']
            juegos = list(db.main_juego.find({'consola_id': consola}))
    else:
        form = BuscarConsolaForm()
    return render(request, 'filtrado.html', {'form': form, 'juegos': juegos, 'filtro': "Consola", 'filtro2': consola})

def filtrarDesarrolladora(request):
    form = BuscarDesarrolladoraForm()
    juegos = []
    desarrolladora = ""
    if request.method == 'POST':
        form = BuscarDesarrolladoraForm(request.POST)
        if form.is_valid():
            desarrolladora = form.cleaned_data['desarrolladora']
            juegosIDs = list(db.main_juego_desarrolladoras.find({'desarrolladora_id': desarrolladora}))
            juego_ids = [juego['juego_id'] for juego in juegosIDs]
            juegos = list(db.main_juego.find({'ranking': {'$in': juego_ids}}))    
    else:
        form = BuscarDesarrolladoraForm()
    return render(request, 'filtrado.html', {'form': form, 'juegos': juegos, 'filtro': "Desarrolladora", 'filtro2': desarrolladora})

def filtrarClasificacion(request):
    form = BuscarClasificacionForm()
    juegos = []
    clasificacion = ""
    if request.method == 'POST':
        form = BuscarClasificacionForm(request.POST)
        if form.is_valid():
            clasificacion = form.cleaned_data['clasificacion']
            juegos = list(db.main_juego.find({'clasificacion_id': clasificacion.id}))
    else:
        form = BuscarClasificacionForm()
    return render(request, 'filtrado.html', {'form': form, 'juegos': juegos, 'filtro': "Clasificación", 'filtro2': clasificacion})

def filtrarFecha(request):
    form = BuscarFechaLanzamientoForm()
    juegos = []
    anyo = ""
    if request.method == 'POST':
        form = BuscarFechaLanzamientoForm(request.POST)
        if form.is_valid():
            anyo = form.cleaned_data['fechaLanzamiento']
            juegos = db.main_juego.find({'fechaLanzamiento': {'$gte': datetime.datetime(int(anyo), 1, 1), '$lt': datetime.datetime(int(anyo)+1, 1, 1)}})
    else:
        form = BuscarFechaLanzamientoForm()
    return render(request, 'filtrado.html', {'form': form, 'juegos': juegos, 'filtro': "Año de Lanzamiento", 'filtro2': anyo})

def filtrarFechaPuntuMeta(request):
    form1= BuscarFechaLanzamientoForm()
    form2= BuscarPuntMetaForm()
    juegos = []
    anyo = ""
    puntMeta = ""
    if request.method == 'POST':
        form1 = BuscarFechaLanzamientoForm(request.POST)
        form2 = BuscarPuntMetaForm(request.POST)
        if form1.is_valid() and form2.is_valid():
            anyo = str(form1.cleaned_data['fechaLanzamiento'])
            puntMeta = form2.cleaned_data['puntMeta']
            juegos = db.main_juego.find({"fechaLanzamiento": {'$gte': datetime.datetime(int(anyo), 1, 1), '$lt': datetime.datetime(int(anyo)+1, 1, 1)}, "puntuacionMeta": {"$gte": puntMeta}})
    else:
        form1 = BuscarFechaLanzamientoForm()
        form2 = BuscarPuntMetaForm()
    return render(request, 'filtradoDoble.html', {'form1': form1, 'form2': form2, 'juegos': juegos, 'filtro': "Año de Lanzamiento y Puntuación Mínima Metacritic", 'filtro2': anyo, 'filtro3': puntMeta})

def filtrarFechaPuntuUsu(request):
    form1= BuscarFechaLanzamientoForm()
    form2= BuscarPuntUsuForm()
    juegos = []
    anyo = ""
    puntUsu = ""
    if request.method == 'POST':
        form1 = BuscarFechaLanzamientoForm(request.POST)
        form2 = BuscarPuntUsuForm(request.POST)
        if form1.is_valid() and form2.is_valid():
            anyo = str(form1.cleaned_data['fechaLanzamiento'])
            puntUsu = form2.cleaned_data['puntUsu']
            juegos = db.main_juego.find({"fechaLanzamiento": {'$gte': datetime.datetime(int(anyo), 1, 1), '$lt': datetime.datetime(int(anyo)+1, 1, 1)}, "puntuacionUsuarios": {"$gte": puntUsu}}).sort("puntuacionUsuarios", DESCENDING)
    else:
        form1 = BuscarFechaLanzamientoForm()
        form2 = BuscarPuntUsuForm()
    return render(request, 'filtradoDoble.html', {'form1': form1, 'form2': form2, 'juegos': juegos, 'filtro': "Año de Lanzamiento y Puntuación Mínima Usuario", 'filtro2': anyo, 'filtro3': puntUsu}) 

def ingresar(request):
    accion = request.get_full_path().split('=')[1]
    if(accion == '/populateWhoosh/'):
        accion = "Crear Índice de Whoosh"
    elif(accion == '/populateBD/'):
        accion = "Poblar Base de Datos"
    if request.user.is_authenticated:
        urlActual = request.get_full_path().split('=')[1]
        return HttpResponseRedirect(urlActual)
    formulario = AuthenticationForm()
    if request.method=='POST':
        formulario = AuthenticationForm(request.POST)
        usuario=request.POST['username']
        clave=request.POST['password']
        acceso=authenticate(username=usuario,password=clave)
        if acceso is not None:
            if acceso.is_active:
                login(request, acceso)
                urlActual = request.get_full_path().split('=')[1]
                return HttpResponseRedirect(urlActual)
            else:
                return render(request, 'ingresar.html',{'titulo':'ERROR','mensaje':"USUARIO NO ACTIVO",'STATIC_URL':settings.STATIC_URL,'accion':accion})
        else:
            return render(request, 'ingresar.html',{'titulo':'ERROR','mensaje':"USUARIO O CONTRASEÑA INCORRECTOS",'STATIC_URL':settings.STATIC_URL,'accion':accion})
                     
    return render(request, 'ingresar.html', {'formulario':formulario, 'STATIC_URL':settings.STATIC_URL, 'accion':accion})

def compararRanking(request):
    form1 = BuscarRankingForm()
    form2 = BuscarRankingComparadorForm()
    ranking1 = ""
    ranking2 = ""
    juego1 = []
    juego2 = []
    if request.method == 'POST':
        form1 = BuscarRankingForm(request.POST)
        form2 = BuscarRankingComparadorForm(request.POST)
        if form1.is_valid() and form2.is_valid():
            ranking1 = form1.cleaned_data['ranking']
            ranking2 = form2.cleaned_data['rankingComparador']
            juego1 = db.main_juego.find({'ranking': ranking1})
            juego2 = db.main_juego.find({'ranking': ranking2})
    else:
        form1 = BuscarRankingForm()
        form2 = BuscarRankingComparadorForm()
    return render(request, 'compararJuegos.html', {'form1': form1, "form2": form2, 'juegos1': juego1, 'juegos2': juego2})