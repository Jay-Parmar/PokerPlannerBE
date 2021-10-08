from django.db import models
from django.utils import timezone

from utils import managers as util_managers


class CommonInfo(models.Model):
    """
    Class containing common fields in all models.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True


class SoftDeletionModel(models.Model):
    """
    Class handling soft deletion of all models.
    """
    deleted_at = models.DateTimeField(blank=True, null=True)

    objects = util_managers.SoftDeletionManager()
    all_objects = util_managers.SoftDeletionManager(alive_only=False)

    class Meta:
        abstract = True

    def delete(self):
        self.deleted_at = timezone.now()
        self.save()

    def hard_delete(self):
        super(SoftDeletionModel, self).delete()
