from django.db import models
from django.utils import timezone

class Extraction_zoom(models.Model):
    created_at = models.DateTimeField(default=timezone.now)
    username = models.CharField(max_length=100, unique=False)
    commentaire = models.CharField(max_length=200, null=True)

    class Meta:
        # Ajouter des contraintes ou des index si nécessaire
        verbose_name = "Extraction_zoom"
        verbose_name_plural = "Extraction_zooms"

    def __str__(self):
        return self.username

    # Exemple de méthode utilitaire
    def get_full_name(self):
        return f"{self.username}"
