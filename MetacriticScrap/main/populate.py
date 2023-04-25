import shutil
import time
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import os, ssl
from user_agent import generate_user_agent
from whoosh.index import create_in
from whoosh.fields import Schema, TEXT, ID
from MetacriticScrap.settings import db

path = "https://www.metacritic.com/browse/games/score/metascore/all/all/filtered?page="

base = "https://www.metacritic.com"

num_pages = 1 #Para una carga de datos completa, poner 200, si se quiere una carga rápida de prueba, probar con un par de páginas

requests.packages.urllib3.disable_warnings()
if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context

def extraer_datos(pagina):
    res = []
    session = requests.Session()
    user_agent=generate_user_agent(device_type="desktop", os=("linux"), navigator=('firefox'))
    session.headers.update({'User-Agent': user_agent})
    
    print("Página " + str(pagina+1) + " de " + str(num_pages))
    url = path + str(pagina)  
    req = session.get(url)
    s = BeautifulSoup(req.text,"lxml")
    games = s.find_all("td", class_="clamp-summary-wrap")
    imagenes = s.find_all("td", class_="clamp-image-wrap")
    while((len(games)!=100 or len(imagenes)!=100) and pagina!=num_pages-1):
        print("Error al obtener los datos de la página " + str(pagina) + ". Volviendo a intentarlo...")
        time.sleep(10)
        user_agent=generate_user_agent(device_type="desktop", os=("win", "mac", "linux"), navigator=('chrome', 'firefox'))
        session.headers.update({'User-Agent': user_agent})
        req = session.get(url)
        s = BeautifulSoup(req.text,"lxml")
        games = s.find_all("td", class_="clamp-summary-wrap")
        imagenes = s.find_all("td", class_="clamp-image-wrap")
    
    for game, imagen in zip(games, imagenes):
        juego = []
        id = game.find("span", class_="title numbered").get_text().strip().split(".")[0]
        print("Juego " + id)
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

        req = session.get(url, verify=False)
        s=BeautifulSoup(req.text,"lxml")
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

def delete_collections():
    db.main_genero.drop()
    db.main_desarrolladora.drop()
    db.main_consola.drop()
    db.main_clasificacion.drop()
    db.main_juego.drop()
    db.main_juego_generos.drop()
    db.main_juego_desarrolladoras.drop()
    db.main_juego_otrasConsolas.drop()

def populate_database():
    delete_collections()
    print('Populando base de datos...')
    i=0
    while(i<num_pages):
        datos = extraer_datos(i)
        i+=1
        for juego in datos:
            consola = db.main_consola.update_one(
                {'nombre': juego[4]},
                {'$setOnInsert': {'nombre': juego[4]}},
                upsert=True
            )
            clasificacion = db.main_clasificacion.update_one(
                {'nombre': juego[12]},
                {'$setOnInsert': {'nombre': juego[12]}},
                upsert=True
            )
            fecha = formatear_fecha(juego[10])
            if(juego[6] == "tbd"):
                juego[6] = 0
            ranking = int(juego[0])
            juego_doc = {
                'ranking': ranking,
                'nombre': juego[1],
                'imagen': juego[2],
                'url': juego[3],
                'consola': juego[4],
                'puntuacionMeta': int(juego[5]),
                'puntuacionUsuarios': float(juego[6]),
                'descripcion': juego[7],
                'urlMetaReviews': juego[8],
                'urlUsuariosReviews': juego[9],
                'fechaLanzamiento': fecha,
                'clasificacion': juego[12]
            }
            db.main_juego.insert_one(juego_doc).inserted_id
            
            for genero in juego[13]:
                if(genero == ""):
                    continue
                db.main_genero.update_one(
                    {'nombre': genero},
                    {'$setOnInsert': {'nombre': genero}},
                    upsert=True
                )
                genero_doc = {
                    'genero': genero,
                    'juego_id': ranking
                }
                db.main_juego_generos.insert_one(genero_doc)
            
            for desarrolladora in juego[11]:
                db.main_desarrolladora.update_one(
                    {'nombre': desarrolladora},
                    {'$setOnInsert': {'nombre': desarrolladora}},
                    upsert=True
                )
                desarrolladora_doc = {
                    'desarrolladora': desarrolladora,
                    'juego_id': ranking
                }
                db.main_juego_desarrolladoras.insert_one(desarrolladora_doc)
            
            for otraConsola in juego[14]:
                otra_consola_doc = {
                    'consola': otraConsola,
                    'juego_id': ranking
                }
                db.main_juego_otrasConsolas.insert_one(otra_consola_doc)
    # Contamos los documentos en cada colección
    generos = db.main_genero.count_documents({})
    desarrolladoras = db.main_desarrolladora.count_documents({})
    consolas = db.main_consola.count_documents({})
    clasificaciones = db.main_clasificacion.count_documents({})
    juegos = db.main_juego.count_documents({})
    print('Finalizada la carga de la base de datos')
    return juegos, generos, desarrolladoras, consolas, clasificaciones

def populate_whoosh():
    schem=Schema(id=ID(stored=True,unique=True), nombre=TEXT(), descripcion=TEXT(stored=False))

    if os.path.exists("Index"):
        shutil.rmtree("Index")
    os.mkdir("Index")

    ix = create_in("Index", schema=schem)
    writer = ix.writer()

    numJuegos=0
    listaJuegos = list(db.main_juego.find())
    for juego in listaJuegos:
        writer.add_document(id=str(juego.ranking), nombre=str(juego.nombre), descripcion=str(juego.descripcion))  
        numJuegos+=1
    writer.commit()
    return numJuegos
    