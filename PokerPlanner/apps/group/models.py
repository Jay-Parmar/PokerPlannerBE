from django.db import models
from django.conf import settings

from utils import models as util_models
from utils import managers as util_managers


class Group(util_models.CommonInfo, util_models.SoftDeletionModel):
    """
    Group model to store group details.
    """
    name = models.CharField(unique=True, max_length=50, help_text="Name of the group")
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="groups_created", on_delete=models.CASCADE)
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='groups_involved', help_text="Members in a group")
    
    def __str__(self):
        return self.name
