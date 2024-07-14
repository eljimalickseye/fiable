from django.db import models
from django.utils import timezone

class Extraction_naf(models.Model):
    created_at = models.DateTimeField(default=timezone.now)
    Name = models.CharField(max_length=50, unique=True)
    Password = models.CharField(max_length=50)
    Profile = models.CharField(max_length=50)
    Locale = models.CharField(max_length=50)
    UserType = models.CharField(max_length=50)
    PasswordUpdateDate = models.DateTimeField(null=True, blank=True)
    Attempts = models.CharField(max_length=200, null=True)
    AccountLocked= models.CharField(max_length=200, null=True)
    LockedTime = models.DateTimeField(null=True, blank=True)
    isFirstPasswordChanged= models.CharField(max_length=200, null=True)
    MailAddress = models.CharField(max_length=200, null=True)
    Description = models.CharField(max_length=200, null=True)
    EmailNotification = models.CharField(max_length=200, null=True)
    commentaire = models.CharField(max_length=200, null=True)

    class Meta:
        # Ajouter des contraintes ou des index si nécessaire
        verbose_name = "Extraction_naf"
        verbose_name_plural = "Extraction_nafs"

    def __str__(self):
        return self.Name

    # Exemple de méthode utilitaire
    def get_full_name(self):
        return f"{self.Name}"
