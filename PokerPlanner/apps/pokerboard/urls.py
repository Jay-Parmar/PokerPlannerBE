from django.urls import include, path
from rest_framework.routers import DefaultRouter

from django.urls import path, include

from apps.pokerboard import views as pokerboard_views

router = DefaultRouter()
router.register('members', pokerboard_views.PokerboardMembersView)
router.register('ticket',pokerboard_views.TicketViewSet)
router.register('vote', pokerboard_views.VoteViewSet)
router.register('', pokerboard_views.PokerBoardViewSet)

urlpatterns = [
    path('',include(router.urls)),
    path('comment',pokerboard_views.CommentView.as_view(), name="comment"),
    path('manager', pokerboard_views.ManagerLoginView.as_view()),
]
