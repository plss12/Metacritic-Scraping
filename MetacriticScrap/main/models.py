from djongo import models
from django.core.validators import URLValidator

class Genero(models.Model):
    nombre = models.CharField(max_length=50, primary_key=True)

    def __str__(self):
        return self.nombre
    
    @classmethod
    def drop_collection(cls):
        cls.objects.all().delete()

class Consola(models.Model):
    nombre = models.CharField(max_length=50, primary_key=True)

    def __str__(self):
        return self.nombre
    
    @classmethod
    def drop_collection(cls):
        cls.objects.all().delete()

class Desarrolladora(models.Model):
    nombre = models.CharField(max_length=50, primary_key=True)

    def __str__(self):
        return self.nombre
    
    @classmethod
    def drop_collection(cls):
        cls.objects.all().delete()

class Clasificacion(models.Model):
    nombre = models.CharField(max_length=5, primary_key=True)

    def __str__(self):
        return self.nombre

    @classmethod
    def drop_collection(cls):
        cls.objects.all().delete()

class Juego(models.Model):
    ranking = models.IntegerField(primary_key=True)
    nombre = models.CharField(max_length=50)
    imagen = models.URLField(validators=[URLValidator()])
    url = models.URLField(validators=[URLValidator()])
    urlMetaReviews = models.URLField(validators=[URLValidator()])
    urlUsuariosReviews = models.URLField(validators=[URLValidator()])
    puntuacionMeta = models.IntegerField()
    puntuacionUsuarios = models.FloatField()
    fechaLanzamiento = models.DateField()
    descripcion = models.CharField(max_length=200)
    generos = models.ManyToManyField(Genero)
    consola = models.ForeignKey(Consola, on_delete=models.CASCADE)
    otrasConsolas = models.ManyToManyField(Consola, related_name='otrasConsolas')
    desarrolladoras = models.ManyToManyField(Desarrolladora)
    clasificacion = models.ForeignKey(Clasificacion, on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre + ' - ' + self.consola.nombre

    @classmethod
    def drop_collection(cls):
        cls.objects.all().delete()