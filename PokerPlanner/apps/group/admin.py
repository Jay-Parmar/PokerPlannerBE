from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from apps.group.models import Group

admin.site.register(Group)
