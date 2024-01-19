from django.urls.conf import path
from rest_framework.routers import DefaultRouter

from apps.group import views as group_views

router = DefaultRouter()
router.register('(?P<group_id>\d+)/removemembers', group_views.GroupDeleteMemberView, basename="members")
router.register('', group_views.GroupViewSet, basename='groups')

urlpatterns = [
        path('addmembers', group_views.GroupAddMemberView.as_view(), name="members"),
] + router.urls
