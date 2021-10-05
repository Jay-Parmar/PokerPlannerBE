from django.db import models
from django.conf import settings
from apps.user.models import CommonInfo


class Group(CommonInfo):
    """
    Group model to store group details.
    """
    name = models.CharField(unique=True, max_length=50, help_text="Name of the group")
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="groups_created", on_delete=models.CASCADE)
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='groups_involved', help_text="Members in a group")
    
    def __str__(self):
        return self.name
