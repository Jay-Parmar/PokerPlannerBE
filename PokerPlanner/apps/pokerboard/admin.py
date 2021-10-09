from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from apps.pokerboard.models import Pokerboard, Ticket

admin.site.register(Pokerboard)
admin.site.register(Ticket)
