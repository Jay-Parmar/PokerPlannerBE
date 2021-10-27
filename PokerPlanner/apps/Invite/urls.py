from rest_framework.routers import DefaultRouter

from django.urls import path, include

from apps.Invite import views

router = DefaultRouter()
router.register('', views.InviteViewSet)

urlpatterns = [
    path("managerinvites/", views.ManagerListInviteView.as_view()),
    path("", include(router.urls)),
]
