from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.pokerboard import views as pokerboard_views

router = DefaultRouter()
router.register('', pokerboard_views.PokerBoardViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path('manager', pokerboard_views.ManagerLoginView.as_view()),
]