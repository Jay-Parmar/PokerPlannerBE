from rest_framework.routers import DefaultRouter

from django.urls import path, include

from apps.Invite import views

router = DefaultRouter()
router.register('', views.InviteViewSet)

urlpatterns = [
    path("", include(router.urls))
]
