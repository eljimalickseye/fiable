from django.db import models
from django.utils import timezone
# Create your models here.

class Groupe_AD(models.Model):
    created_at = models.DateTimeField(default=timezone.now)
    display_name = models.CharField(max_length=100,null=True)
    sam_account_name = models.CharField(max_length=100, null=True) #username
    email_address = models.CharField(max_length=100, null=True)
    account_status = models.CharField(max_length=100,null=True) #status
    commentaire = models.CharField(max_length=100,null=True)

    class Meta:
        # Ajouter des contraintes ou des index si nécessaire
        verbose_name = "Groupe_AD"
        verbose_name_plural = "Groupe_ADs"
    
    def __str__(self):
        return self.sam_account_name