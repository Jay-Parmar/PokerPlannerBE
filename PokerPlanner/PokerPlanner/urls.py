from django.contrib import admin
from django.urls import path
from django.urls.conf import include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include('apps.user.urls')),
    path('pokerboard/', include('apps.pokerboard.urls')),
    path('group/',include('apps.group.urls'))
]
