# -*- coding: utf-8 -*-

from django.urls import path
from .views.invitation import invitation_router
from .views import account
urlpatterns = [
    # Invitation Related API
    path('subject/<int:id>/invite', invitation_router),
    # Account Related API
    path('account/login/', account.login),
    path('account/add/', account.add),
    path('account/update/', account.update),
    path('account/delete/', account.delete),
    path('account/invite/accept/', account.invite_accept),
    path('account', account.account),
]


