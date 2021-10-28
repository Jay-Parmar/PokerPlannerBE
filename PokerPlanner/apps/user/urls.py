from django.urls.conf import include, path
from rest_framework.routers import DefaultRouter

from apps.user import views as user_views

router = DefaultRouter()

urlpatterns = [
    path('',user_views.UserViewSet.as_view()),
    path('login/', user_views.LoginView.as_view(), name="login"),
    path('logout/', user_views.LogoutView.as_view(), name="logout"),
    path('changepassword/', user_views.ChangePasswordView.as_view()),
    path('activate/<slug:pk>', user_views.ActivateAccountView.as_view(), name='activate'),
    path('resend', user_views.ResendEmailView.as_view(), name='resend')
] 
