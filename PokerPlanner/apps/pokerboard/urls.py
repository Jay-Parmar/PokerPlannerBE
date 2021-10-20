from rest_framework.routers import DefaultRouter

from django.urls import path, include

from apps.pokerboard.views import ManagerLoginView, PokerBoardViewSet

router = DefaultRouter()
router.register('', PokerBoardViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path('manager', ManagerLoginView.as_view()),
]