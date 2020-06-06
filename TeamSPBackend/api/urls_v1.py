# -*- coding: utf-8 -*-

from django.urls import path
from .views.invitation import invitation_router
from .views.account import account_router, login, update_account, delete, invite_accept
from .views.subject import subject_router, update_subject, delete_subject

urlpatterns = [
    # Invitation Related API
    path('subject/<int:id>/invite', invitation_router),
    # Account Related API
    path('account/login', login),
    path('account/update', update_account),
    path('account/delete', delete),
    path('account', account_router),
    path('subject/invite/accept', invite_accept),

    # Subject Related API
    path('subject', subject_router),
    path('subject/<int:id>', subject_router),
    path('subject/<int:id>/update', update_subject),
    path('subject/<int:id>/delete', delete_subject),
]
