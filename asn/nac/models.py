from django.db import models
from django.utils import timezone

class Extraction_nac(models.Model):
    created_at = models.DateTimeField(default=timezone.now)
    Name = models.CharField(max_length=150,null=True, blank=True)
    Password = models.CharField(max_length=150,null=True, blank=True)
    Profile = models.CharField(max_length=150,null=True, blank=True)
    Locale = models.CharField(max_length=150,null=True, blank=True)
    Description = models.CharField(max_length=150,null=True, blank=True)
    UserType = models.CharField(max_length=150,null=True, blank=True)
    PasswordUpdateDate = models.DateTimeField(null=True, blank=True)
    MailAddress = models.CharField(max_length=200, null=True)
    commentaire = models.CharField(max_length=200, null=True)

    class Meta:
        # Ajouter des contraintes ou des index si nécessaire
        verbose_name = "Extraction_nac"
        verbose_name_plural = "Extraction_nacs"

    def __str__(self):
        return self.Name

    # Exemple de méthode utilitaire
    def get_full_name(self):
        return f"{self.Name}"
