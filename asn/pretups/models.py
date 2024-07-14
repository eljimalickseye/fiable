from django.db import models
from django.utils import timezone


class Extraction_pretups(models.Model):
    created_at = models.DateTimeField(default=timezone.now, blank=True)
    login_id = models.CharField(max_length=100,null=True)
    user_name = models.CharField(max_length=100,null=True)
    msisdn = models.CharField(max_length=100,null=True)
    status = models.CharField(max_length=100,null=True)
    last_login_on = models.DateTimeField(null=True, blank=True)
    last_login_on_char = models.CharField(max_length=100,null=True)
    employee_code = models.CharField(max_length=100, null=True)
    user_type = models.CharField(max_length=100, null=True)
    modified_on = models.CharField(max_length=100, null=True)
    created_on = models.CharField(max_length=100, null=True)
    role_code = models.CharField(max_length=100, null=True)
    group_role_code = models.CharField(max_length=100, null=True)
    role_name = models.CharField(max_length=100, null=True)
    parent_user_name = models.CharField(max_length=100, null=True, blank=True)
    parent_msisdn = models.CharField(max_length=20, null=True, blank=True)
    commentaire = models.CharField(max_length=100,null=True)
    traitement = models.CharField(max_length=100,null=True)



    class Meta:
        # Ajouter des contraintes ou des index si nécessaire
        verbose_name = "Extraction_pretups"
        verbose_name_plural = "Extraction_pretupss"

    def __str__(self):
        return self.login_id

    # Exemple de méthode utilitaire
    def get_full_name(self):
        return f"{self.login_id}"
