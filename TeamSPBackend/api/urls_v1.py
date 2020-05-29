# -*- coding: utf-8 -*-

from django.urls import path
from .views.invitation import invitation_router
from django.conf.urls import url
from .views import account
urlpatterns = [
    # Invitation Related API
    path('subject/<int:id>/invite', invitation_router),
    url(r'^account/login/', account.login),
    url(r'^account/add/', account.add),
    url(r'^account/update/', account.update),
    url(r'^account/delete/', account.delete),
    url(r'^account/invite/accept', account.invite_accept),
    url(r'^account/', account.account)
]


