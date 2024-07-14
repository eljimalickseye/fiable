from django.db import models
from django.utils import timezone

class Extraction_ussd_osn(models.Model):
    created_at = models.DateTimeField(default=timezone.now)
    User = models.CharField(max_length=75, unique=True)
    Groups = models.CharField(max_length=500)
    commentaire = models.CharField(max_length=150, null=True)


    class Meta:
        # Ajouter des contraintes ou des index si nécessaire
        verbose_name = "Extraction_ussd_osn"
        verbose_name_plural = "Extraction_ussd_osns"

    def __str__(self):
        return self.User

    # Exemple de méthode utilitaire
    def get_full_name(self):
        return f"{self.User}"
