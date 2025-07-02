from django.db import models

class Utente(models.Model):
    mail = models.CharField(max_length=255, blank=True, null=True)
    password = models.CharField(max_length=255, blank=True, null=True)
    nome = models.CharField(max_length=100, blank=True, null=True)
    reset_token = models.CharField(max_length=255, blank=True, null=True)
    reset_expire = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'utente'

