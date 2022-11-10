from django.db import models
from django.contrib.auth.models import User

class Item(models.Model):
    nombre = models.CharField(max_length=50)
    descripcion = models.TextField()
    url_icono = models.URLField(verbose_name="URL del icono")
    url = models.URLField(verbose_name="URL del objeto")
    ilvl = models.IntegerField(verbose_name="Nivel de objeto")
    slot = models.CharField(max_length=20)
    tipo = models.CharField(max_length=20)

    def _str__(self):
        return self.nombre

class UserItem(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def _str__(self):
        return str(self.user.id) + "-" + self.item.nombre

    class Meta:
        unique_together = ('item', 'user',)

class Keyword(models.Model):
    keyword = models.CharField(max_length=50)

    def _str__(self):
        return self.keyword

