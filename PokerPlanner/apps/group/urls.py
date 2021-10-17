from django.urls.conf import path

from rest_framework.routers import DefaultRouter

from apps.group import views as group_views

router = DefaultRouter()
router.register('', group_views.GroupViewSet)

urlpatterns = [
        path('add', group_views.AddGroupMemberView.as_view(), name="add"),
        path('remove', group_views.RemoveGroupMemberView.as_view(), name="remove")

] + router.urls
