from django.db import models
from django.utils import timezone
# Create your models here.

class Extraction_ams(models.Model):
    created_at = models.DateTimeField(default=timezone.now)
    user_id = models.CharField(max_length=100,null=True)
    full_user_name = models.CharField(max_length=100, null=True)
    email_address = models.CharField(max_length=100, null=True)
    description = models.CharField(max_length=100, null=True)
    password = models.CharField(max_length=100,null=True)
    change_password = models.CharField(max_length=100,null=True)
    bypass_password = models.CharField(max_length=100,null=True)
    roles=models.CharField(max_length=100,null=True)
    allowed_pap_group = models.CharField(max_length=100,null=True)
    use_global_max_number_of_concurrent_sessions = models.CharField(max_length=100,null=True)
    locked=models.CharField(max_length=100,null=True)
    commentaire = models.CharField(max_length=100,null=True)

    class Meta:
        # Ajouter des contraintes ou des index si nécessaire
        verbose_name = "Extraction_ams"
        verbose_name_plural = "Extraction_ams"
    
    def __str__(self):
        return self.user_id