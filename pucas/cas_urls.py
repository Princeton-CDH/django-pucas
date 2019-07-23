from django.conf.urls import url
from django_cas_ng.views import LoginView, LogoutView, CallbackView

urlpatterns = [
    url(r'^login/$', LoginView.as_view(), name='cas_ng_login'),
    url(r'^logout/$', LogoutView.as_view(), name='cas_ng_logout'),
    url(r'^callback/$', CallbackView.as_view(), name='cas_ng_proxy_callback'),
]
