from rest_framework.routers import DefaultRouter

from django.urls import path, include

from apps.pokerboard import views as PokerboardViews

router = DefaultRouter()
router.register('members', PokerboardViews.PokerboardMembersView)
router.register('', PokerboardViews.PokerBoardViewSet)

urlpatterns = [
    path('',include(router.urls)),
    path('manager', PokerboardViews.ManagerLoginView.as_view()),
]