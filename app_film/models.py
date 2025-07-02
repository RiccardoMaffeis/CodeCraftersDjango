# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models

class Film(models.Model):
    codice = models.IntegerField(primary_key=True)
    titolo = models.CharField(max_length=37, blank=True, null=True)
    anno = models.IntegerField(blank=True, null=True)
    durata = models.IntegerField(blank=True, null=True)
    lingua = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'film'
        
class Sala(models.Model):
    numero = models.IntegerField(primary_key=True)
    numposti = models.IntegerField(db_column='numPosti', blank=True, null=True)  # Field name made lowercase.
    dim = models.IntegerField(blank=True, null=True)
    numfile = models.IntegerField(db_column='numFile', blank=True, null=True)  # Field name made lowercase.
    numpostiperfila = models.IntegerField(db_column='numPostiPerFila', blank=True, null=True)  # Field name made lowercase.
    tipo = models.CharField(max_length=12, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'sala'

class Proiezione(models.Model):
    numproiezione = models.CharField(db_column='numProiezione', primary_key=True, max_length=17)  # Field name made lowercase.
    sala = models.ForeignKey(
        Sala,
        on_delete=models.CASCADE,
        db_column='sala', 
        related_name='proiezioni',
        blank=True,
        null=True
    )
    filmproiettato = models.ForeignKey(
        Film,
        on_delete=models.CASCADE,
        db_column='filmProiettato',
        related_name='proiezioni',
        blank=True,
        null=True
    )
    data = models.CharField(max_length=10, blank=True, null=True)
    ora = models.CharField(max_length=8, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'proiezione'

