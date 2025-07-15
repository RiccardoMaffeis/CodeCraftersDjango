# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Biglietto(models.Model):
    numproiezione = models.CharField(db_column='numProiezione', max_length=50, blank=True, null=True)  # Field name made lowercase.
    numfila = models.CharField(db_column='numFila', max_length=10, blank=True, null=True)  # Field name made lowercase.
    numposto = models.IntegerField(db_column='numPosto', blank=True, null=True)  # Field name made lowercase.
    datavendita = models.DateField(db_column='dataVendita', blank=True, null=True)  # Field name made lowercase.
    prezzo = models.CharField(max_length=50, blank=True, null=True)
    email = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Biglietto'

