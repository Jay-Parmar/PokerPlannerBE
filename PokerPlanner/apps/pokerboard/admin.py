from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from apps.pokerboard.models import Pokerboard, Ticket, Invite, PokerboardUser, ManagerCredentials

admin.site.register(Pokerboard)
admin.site.register(Ticket)
admin.site.register(Invite)
admin.site.register(PokerboardUser)
admin.site.register(ManagerCredentials)
