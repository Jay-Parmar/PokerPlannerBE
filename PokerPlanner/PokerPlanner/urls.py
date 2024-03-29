from django.contrib import admin
from django.urls import path
from django.urls.conf import include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include('apps.user.urls')),
    path('pokerboard/', include('apps.pokerboard.urls')),
    path('groups/', include('apps.group.urls')),
    path('invite/', include('apps.Invite.urls')),
]
