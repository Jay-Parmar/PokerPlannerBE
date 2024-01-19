from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from apps.pokerboard.models import (Invite, ManagerCredentials, Pokerboard,
                                    PokerboardUser, Ticket, UserTicketEstimate)

admin.site.register(Pokerboard)
admin.site.register(Ticket)
admin.site.register(Invite)
admin.site.register(PokerboardUser)
admin.site.register(ManagerCredentials)
admin.site.register(UserTicketEstimate)
