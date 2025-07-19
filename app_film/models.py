# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models

# Modello per rappresentare un Film
class Film(models.Model):
    # Chiave primaria: codice identificativo del film
    codice = models.IntegerField(primary_key=True)
    
    # Titolo del film (opzionale)
    titolo = models.CharField(max_length=37, blank=True, null=True)
    
    # Anno di uscita del film (opzionale)
    anno = models.IntegerField(blank=True, null=True)
    
    # Durata del film in minuti (opzionale)
    durata = models.IntegerField(blank=True, null=True)
    
    # Lingua originale del film (opzionale)
    lingua = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        # Django non gestisce direttamente questa tabella
        managed = False
        
        # Nome tabella nel database
        db_table = 'Film'
        
# Modello per rappresentare una Sala cinematografica
class Sala(models.Model):
    # Chiave primaria: numero identificativo della sala
    numero = models.IntegerField(primary_key=True)
    
    # Numero totale di posti a sedere (opzionale)
    numposti = models.IntegerField(db_column='numPosti', blank=True, null=True)
    
    # Dimensione della sala (opzionale)
    dim = models.IntegerField(blank=True, null=True)
    
    # Numero di file di sedili nella sala (opzionale)
    numfile = models.IntegerField(db_column='numFile', blank=True, null=True)
    
    # Numero di posti per ogni fila (opzionale)
    numpostiperfila = models.IntegerField(db_column='numPostiPerFila', blank=True, null=True)
    
    # Tipo di sala (es. "3-D", "tradizionale", ecc.) (opzionale)
    tipo = models.CharField(max_length=12, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Sala'

# Modello per rappresentare una Proiezione (singolo spettacolo di un film)
class Proiezione(models.Model):
    # Chiave primaria: identificatore univoco della proiezione
    numproiezione = models.CharField(db_column='numProiezione', primary_key=True, max_length=17)
    
    # Sala dove si svolge la proiezione (collegamento alla tabella Sala)
    sala = models.ForeignKey(
        Sala,
        on_delete=models.CASCADE,  # Elimina la proiezione se la sala viene eliminata
        db_column='sala', 
        related_name='proiezioni',
        blank=True,
        null=True
    )
    
    # Film proiettato (collegamento alla tabella Film)
    filmproiettato = models.ForeignKey(
        Film,
        on_delete=models.CASCADE,  # Elimina la proiezione se il film viene eliminato
        db_column='filmProiettato',
        related_name='proiezioni',
        blank=True,
        null=True
    )
    
    # Data della proiezione (formato stringa, es. "17/07/2025")
    data = models.CharField(max_length=10, blank=True, null=True)
    
    # Ora della proiezione (formato stringa, es. "20:30")
    ora = models.CharField(max_length=8, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Proiezione'
