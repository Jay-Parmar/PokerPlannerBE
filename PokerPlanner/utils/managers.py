from django.db import models
from django.db.models.query import QuerySet
from django.utils import timezone


class SoftDeletionQuerySet(QuerySet):
    """
    Soft Deletion queryset class.
    """
    def delete(self):
        return super(SoftDeletionQuerySet, self).update(deleted_at=timezone.now())

    def hard_delete(self):
        return super(SoftDeletionQuerySet, self).delete()

    def restore(self):
        return super(SoftDeletionQuerySet, self).update(deleted_at=None)


class SoftDeletionManager(models.Manager):
    """
    Manager for Soft Deletion abstract Model.
    """
    use_for_related_fields = True
    
    def __init__(self, *args, **kwargs):
        self.alive_only = kwargs.pop('alive_only', True)
        super(SoftDeletionManager, self).__init__(*args, **kwargs)

    def get_queryset(self):
        if self.alive_only:
            return SoftDeletionQuerySet(self.model).filter(deleted_at=None)
        return SoftDeletionQuerySet(self.model)

    def hard_delete(self):
        return self.get_queryset().hard_delete()

    def delete(self):
        if self.alive_only:
            return SoftDeletionQuerySet(self.model).delete()
        return SoftDeletionQuerySet(self.model).hard_delete()

    def restore(self):
        return self.get_queryset().restore()
