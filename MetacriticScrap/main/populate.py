import shutil
from main.models import Genero, Consola, Desarrolladora, Clasificacion, Juego
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import os, ssl
from user_agent import generate_user_agent
from whoosh.index import create_in
from whoosh.fields import Schema, TEXT, ID

path = "https://www.metacritic.com/browse/games/score/metascore/all/all/filtered?page="

base = "https://www.metacritic.com"

num_pages = 200 #Para una carga de datos completa, poner 200, si se quiere una carga rápida, poner 5 o ménos, ya que por cada página se obtienen 100 juegos

if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context

def extraer_datos():
    res = []
    for i in range(0, num_pages):
        url = path + str(i)
        user_agent = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'User-Agent': generate_user_agent(device_type="desktop", os=('mac', 'linux', 'win'))}
        response = requests.get(url, headers = user_agent) 
        s = BeautifulSoup(response.text,"lxml")
        games = s.find_all("td", class_="clamp-summary-wrap")
        imagenes = s.find_all("td", class_="clamp-image-wrap")
        for game, imagen in zip(games, imagenes):
            juego = []
            id = game.find("span", class_="title numbered").get_text().strip().split(".")[0]
            imagenUrl = imagen.find("img").get("src")
            nombre = game.find("a", class_="title").get_text().strip()
            consola = game.find("div", class_="platform").find("span",class_="data").get_text().strip()
            puntuacionMeta = game.find("div", class_="clamp-metascore").find("div", class_="metascore_w").get_text()
            puntuacionUsuarios = game.find("div", class_="clamp-userscore").find("div", class_="metascore_w").get_text()
            descripcion = game.find("div", class_="summary").get_text().strip()
            urlCriticasMeta = base + game.find("div", class_="clamp-metascore").find("a").get("href")
            urlCriticasUsuarios = base + game.find("div", class_="clamp-userscore").find("a").get("href")
            fechaLanzamiento = game.find("div", class_="clamp-details").find("span",class_="").get_text().strip()
            url = base + game.find("a", class_="title").get("href")
            juego.extend([id, nombre, imagenUrl, url, consola, puntuacionMeta, puntuacionUsuarios, descripcion, urlCriticasMeta, urlCriticasUsuarios, fechaLanzamiento])
            url = base + game.find("a", class_="title").get("href")
            response = requests.get(url, headers = user_agent)
            s = BeautifulSoup(response.text,"lxml")
            desarrolladoras = []
            try:
                desarrolladorasData = s.find("div", class_="summary_wrap").find("div", class_="section product_details").find("div", class_="details side_details").find("li", class_="summary_detail developer").find("span", class_="data").get_text().strip().split(", ")
            except:
                desarrolladorasData = []
            for desarrolladora in desarrolladorasData:
                desarrolladoras.append(desarrolladora.strip())
            try:
                clasificacion = s.find("div", class_="summary_wrap").find("div", class_="section product_details").find("div", class_="details side_details").find("li", class_="summary_detail product_rating").find("span", class_="data").get_text().strip()
            except:
                clasificacion = "No clasificado"
            generos = []
            try:
                generosData = s.find("div", class_="summary_wrap").find("div", class_="section product_details").find("div", class_="details side_details").find("li", class_="summary_detail product_genre").find_all("span", class_="data")
            except:
                generosData = []
            for genero in generosData:
                if(genero!=""):
                    generos.append(genero.get_text().strip())
            otrasConsolas = []
            try:
                otrasConsolasData = s.find("li", class_="summary_detail product_platforms").find("span", class_="data").find_all("a")
                for otraConsola in otrasConsolasData:
                    otrasConsolas.append(otraConsola.get_text().strip())
            except:
                otrasConsolas = []
            juego.extend([desarrolladoras, clasificacion, generos, otrasConsolas])
            res.append(juego)
    return res

def formatear_fecha(fecha):
    fecha = fecha.split(" ")
    res = ""
    if(fecha[0] == "January"):
        res = "01"
    elif(fecha[0] == "February"):
        res = "02"
    elif(fecha[0] == "March"):
        res = "03"
    elif(fecha[0] == "April"):
        res = "04"
    elif(fecha[0] == "May"):
        res = "05"
    elif(fecha[0] == "June"):
        res = "06"
    elif(fecha[0] == "July"):
        res = "07"
    elif(fecha[0] == "August"):
        res = "08"
    elif(fecha[0] == "September"):
        res = "09"
    elif(fecha[0] == "October"):
        res = "10"
    elif(fecha[0] == "November"):
        res = "11"
    elif(fecha[0] == "December"):
        res = "12"
    res += "/" + fecha[1].replace(",","") + "/" + fecha[2]
    fecha = datetime.strptime(res, '%m/%d/%Y')
    return fecha

def delete_tables():
    Genero.objects.all().delete()
    Consola.objects.all().delete()
    Desarrolladora.objects.all().delete()
    Clasificacion.objects.all().delete()
    Juego.objects.all().delete()

def populate_database():
    delete_tables()
    print('Populating database...')
    juegos = 0
    datos = extraer_datos()
    for juego in datos:
        juegos += 1
        print(juego)
        consola = Consola.objects.get_or_create(nombre=juego[4])[0]
        clasificacion = Clasificacion.objects.get_or_create(nombre=juego[12])[0]
        fecha = formatear_fecha(juego[10])
        if(juego[6] == "tbd"):
            juego[6] = 0
        Juego.objects.get_or_create(id=int(juego[0]), nombre=juego[1], imagen=juego[2], url=juego[3], consola=consola, puntuacionMeta=int(juego[5]), puntuacionUsuarios=float(juego[6]), descripcion=juego[7], urlMetaReviews=juego[8], urlUsuariosReviews=juego[9], fechaLanzamiento=fecha, clasificacion=clasificacion)
        for genero in juego[13]:
            genero = Genero.objects.get_or_create(nombre=genero)[0]
            Juego.objects.get(id=juego[0]).generos.add(genero)
        for desarrolladora in juego[11]:
            desarrolladora = Desarrolladora.objects.get_or_create(nombre=desarrolladora)[0]
            Juego.objects.get(id=juego[0]).desarrolladoras.add(desarrolladora)
        for otraConsola in juego[14]:
            consola = Consola.objects.get_or_create(nombre=otraConsola)[0]
            Juego.objects.get(id=juego[0]).otrasConsolas.add(consola)
    generos = Genero.objects.all().count()
    desarrolladoras = Desarrolladora.objects.all().count()
    consolas = Consola.objects.all().count()
    clasificaciones = Clasificacion.objects.all().count()
    print('Finished database population')
    return juegos, generos, desarrolladoras, consolas, clasificaciones

def populate_whoosh():
    #schem=Schema(id=ID(stored=True,unique=True), nombre=TEXT(stored=True), imagen=TEXT(stored=True), url=TEXT(stored=True), consola=TEXT(stored=True), puntuacionMeta=NUMERIC(stored=True), puntuacionUsuarios=NUMERIC(stored=True), descripcion=TEXT(stored=True), urlMetaReviews=TEXT(stored=True), urlUsuariosReviews=TEXT(stored=True), fechaLanzamiento=DATETIME(stored=True), desarrolladoras=TEXT(stored=True), clasificacion=TEXT(stored=True), generos=TEXT(stored=True), otrasConsolas=TEXT(stored=True))
    schem=Schema(id=ID(stored=True,unique=True), nombre=TEXT(), descripcion=TEXT(stored=False))

    if os.path.exists("Index"):
        shutil.rmtree("Index")
    os.mkdir("Index")

    ix = create_in("Index", schema=schem)
    writer = ix.writer()

    numJuegos=0
    listaJuegos=Juego.objects.all()
    for juego in listaJuegos:
        writer.add_document(id=str(juego.id), nombre=str(juego.nombre), descripcion=str(juego.descripcion))  
        numJuegos+=1
    writer.commit()
    return numJuegos
    