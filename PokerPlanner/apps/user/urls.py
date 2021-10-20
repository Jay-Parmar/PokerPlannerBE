from django.urls.conf import path

from rest_framework.routers import DefaultRouter

from apps.user import views as user_views

router = DefaultRouter()
# router.register('', user_views.UserViewSet)

urlpatterns = [
    path('', user_views.UserViewSet.as_view(), name=''),
    path('login/', user_views.Login.as_view(), name="login"),
    path('logout/', user_views.Logout.as_view(), name="logout"),
    path('activate/<slug:pk>', user_views.ActivateAccountView.as_view(), name='activate'),
    path('changepassword/<int:pk>/', user_views.ChangePasswordView.as_view())

] + router.urls
