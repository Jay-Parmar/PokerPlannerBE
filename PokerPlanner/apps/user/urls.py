from django import urls
from django.urls.conf import include, path
from rest_framework.routers import DefaultRouter
from apps.user.views import Login, Logout, UserViewSet, ChangePasswordView

router = DefaultRouter()
# router.register('', UserViewSet)

urlpatterns = [
    path('',UserViewSet.as_view()),
    path('login/', Login.as_view(), name="login"),
    path('logout/', Logout.as_view(), name="logout"),
    path('changepassword/<int:pk>/', ChangePasswordView.as_view())
] 
