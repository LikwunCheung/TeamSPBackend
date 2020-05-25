# -*- coding: utf-8 -*-

from django.urls import path
from .views.invitation import invitation_router

urlpatterns = [
    # Invitation Related API
    path('subject/<int:id>/invite', invitation_router)
]