from django.db import models

# Models que definem o banco de dados

class Rota(models.Model):
    codigo = models.CharField(max_length=10, unique=True) 
    nome  = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.codigo} - {self.nome}"    


class ParadaOnibus(models.Model):
    endereco = models.CharField(max_length=200)
    rotas = models.ManyToManyField(Rota, related_name='pontos')
    latitude = models.FloatField(default=0.0)
    longitude = models.FloatField(default=0.0)

    def __str__(self):
        return self.endereco


class CategoriaMarco(models.Model):
    # Ex: "Visual", "Turístico", "Funcional"
    nome = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.nome





    
