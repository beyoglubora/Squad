from django.urls import path
from django.conf.urls import url

from . import views


urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('activate/', views.account_activation, name='account_activation'),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.activate, name='activate'),
]
