from django.db import models

# Modello che rappresenta un utente personalizzato
class Utente(models.Model):
    # Email dell'utente (può essere nulla o vuota)
    mail = models.CharField(max_length=255, blank=True, null=True)
    
    # Password criptata (può essere nulla o vuota)
    password = models.CharField(max_length=255, blank=True, null=True)
    
    # Nome dell'utente (può essere nullo o vuoto)
    nome = models.CharField(max_length=100, blank=True, null=True)
    
    # Token per il reset della password (null se non attivo)
    reset_token = models.CharField(max_length=255, blank=True, null=True)
    
    # Data e ora di scadenza del token di reset (null se non attivo)
    reset_expire = models.DateTimeField(blank=True, null=True)

    class Meta:
        # Indica che questo modello non verrà gestito da Django (nessuna migrazione automatica)
        managed = False
        
        # Nome della tabella nel database esistente
        db_table = 'Utente'
