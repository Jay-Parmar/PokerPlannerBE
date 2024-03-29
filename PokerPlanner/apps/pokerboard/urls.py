from posixpath import basename
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from django.urls import path, include

from apps.pokerboard import views as pokerboard_views

router = DefaultRouter()
router.register('members', pokerboard_views.PokerboardMembersView)
router.register('ticket',pokerboard_views.TicketViewSet)
router.register('vote', pokerboard_views.VoteViewSet)
router.register('userestimate', pokerboard_views.UserTicketEstimateRetrieveView, basename='estimate')
router.register('', pokerboard_views.PokerBoardViewSet, basename='pokerboard')

urlpatterns = [
    path('managercredentials/update', pokerboard_views.ManagerUpdateCredentialsView.as_view()),
    path('managercredentials', pokerboard_views.ManagerListCredentialView.as_view()),
    path('ordertickets', pokerboard_views.TicketOrderApiView.as_view()),
    path('',include(router.urls)),
    path('comment', pokerboard_views.CommentView.as_view(), name="comment"),
    path('manager', pokerboard_views.ManagerCreateView.as_view()),
    path('jiraticket', pokerboard_views.TicketDetailView.as_view()),
]
