from django.conf import settings
from django.db import models

from libs import models as util_models


class Group(util_models.CommonInfo, util_models.SoftDeletionModel):
    """
    Group model to store group details.
    """
    name = models.CharField(unique=True, max_length=50, help_text="Name of the group")
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="groups_created", on_delete=models.CASCADE)
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='groups_involved', help_text="Members in a group")
    
    def __str__(self):
        return self.name
