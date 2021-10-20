from django.urls.conf import include, path
from rest_framework.routers import DefaultRouter

from apps.user.views import Login, Logout, UserViewSet, ChangePasswordView, ListInvite

router = DefaultRouter()
router.register('', ListInvite)

urlpatterns = [
    path('',UserViewSet.as_view()),
    path('invite/',include(router.urls)),
    path('login/', Login.as_view(), name="login"),
    path('logout/', Logout.as_view(), name="logout"),
    path('changepassword/', ChangePasswordView.as_view())
] 
