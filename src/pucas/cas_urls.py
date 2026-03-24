from django.urls import path
from django_cas_ng.views import LoginView, LogoutView, CallbackView

urlpatterns = [
    path("login/", LoginView.as_view(), name="cas_ng_login"),
    path("logout/", LogoutView.as_view(), name="cas_ng_logout"),
    path("callback/", CallbackView.as_view(), name="cas_ng_proxy_callback"),
]
