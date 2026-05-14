from django.db import models

# Models que definem o banco de dados

class Rotas(models.Model):
    codigo = models.CharField(max_length=10, unique=True) 
    nome  = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.codigo} - {self.nome}"    


class ParadasOnibus(models.Model):
    endereco = models.CharField(max_length=200)
    rotas = models.ManyToManyField(Rotas, related_name='pontos')

    def __str__(self):
        return self.endereco

    
