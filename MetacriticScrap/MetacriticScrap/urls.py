#encoding:utf-8

from django.contrib import admin
from django.urls import path
from main import views

urlpatterns = [
    path('', views.index),
    path('todosJuegos/<int:number>', views.todosJuegos),
    path('juegosRecientes/', views.juegosRecientes),
    path('mejoresJuegos/', views.mejoresJuegos),
    path('mejoresJuegosUsu/', views.mejoresJuegosUsu),
    path('listaConsolas/', views.listaConsolas),
    path('listaDesarrolladoras/', views.listaDesarrolladoras),
    path('listaGeneros/', views.listaGeneros),
    path('listaClasificaciones/', views.listaClasificaciones),
    path('populateBD/', views.populateDB),
    path('populateWhoosh/', views.populateWhoosh),
    path('admin/', admin.site.urls),
    path('juego/<int:id>', views.pagina_juego),
    path('buscarNombre/', views.buscarNombre),
    path('buscarDescripcion/', views.buscarDescripcion),
    path('filtrarGenero/', views.filtrarGenero),
    path('filtrarConsola/', views.filtrarConsola),
    path('filtrarDesarrolladora/', views.filtrarDesarrolladora),
    path('filtrarClasificacion/', views.filtrarClasificacion),
    path('buscarRanking/', views.buscarRanking),
    path('filtrarPuntMeta/', views.filtrarPuntMeta),
    path('filtrarPuntUsu/', views.filtrarPuntUsu),
    path('filtrarFecha/', views.filtrarFecha),
    path('filtrarFechaPuntuMeta/', views.filtrarFechaPuntuMeta),
    path('filtrarFechaPuntuUsu/', views.filtrarFechaPuntuUsu),
    path('ingresar/', views.ingresar),
    path('Consolas/<str:consola>', views.consolaFiltro),
    path('Desarrolladoras/<str:desarrolladora>', views.desarrolladoraFiltro),
    path('Generos/<str:genero>', views.generoFiltro),
    path('Clasificaciones/<str:clasificacion>', views.clasificacionFiltro), 
    path('compararRanking/', views.compararRanking),
]
