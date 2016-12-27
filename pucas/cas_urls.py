from django.conf.urls import url
from django_cas_ng.views import login, logout, callback

urlpatterns = [
    url(r'^login/$', login, name='cas_ng_login'),
    url(r'^logout/$', logout, name='cas_ng_logout'),
    url(r'^callback/$', callback, name='cas_ng_proxy_callback'),
]
