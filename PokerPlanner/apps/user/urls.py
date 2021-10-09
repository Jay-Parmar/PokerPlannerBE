from django import urls
from django.urls.conf import include, path
from rest_framework.routers import DefaultRouter
from apps.user.views import Login, Logout, UserViewSet

router = DefaultRouter()
router.register('', UserViewSet)

urlpatterns = [
    path('/',include(router.urls)),
    path('login/', Login.as_view(), name="login"),
    path('logout/', Logout.as_view(), name="logout")
] + router.urls
