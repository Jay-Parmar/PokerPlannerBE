from django.urls.conf import path
from rest_framework.routers import DefaultRouter
from apps.user.views import Login, Logout, UserViewSet

router = DefaultRouter()
router.register('', UserViewSet)

urlpatterns = [
    path('login/', Login.as_view(), name="login"),
    path('logout/', Logout.as_view(), name="logout")
] + router.urls
