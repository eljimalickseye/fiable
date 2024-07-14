from django.db import models
from django.utils import timezone
# Create your models here.

class Extraction_zsmart(models.Model):
    created_at = models.DateTimeField(default=timezone.now)
    compte = models.CharField(max_length=100,null=True)
    nom = models.CharField(max_length=100, null=True)
    statut_compte = models.CharField(max_length=100, null=True)
    date_creation = models.CharField(max_length=100, null=True)
    verrouille = models.CharField(max_length=100,null=True)
    profil = models.CharField(max_length=100,null=True)
    commentaire = models.CharField(max_length=100,null=True)

    class Meta:
        # Ajouter des contraintes ou des index si nécessaire
        verbose_name = "Extraction_zsmart"
        verbose_name_plural = "Extraction_zsmarts"
    
    def __str__(self):
        return self.compte