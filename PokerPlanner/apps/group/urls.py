from django.urls.conf import path

from rest_framework.routers import DefaultRouter

from apps.group import views as group_views

router = DefaultRouter()
router.register('', group_views.GroupViewSet)

urlpatterns = [
    
] + router.urls
