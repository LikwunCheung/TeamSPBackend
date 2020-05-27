# -*- coding: utf-8 -*-

from django.urls import path
from .views.invitation import invitation_router
from .views.supervisors import supervisors_router
urlpatterns = [
    # Invitation Related API
    path('subject/<int:id>/invite', invitation_router),
    # Invitation Related API
    path('subject/<int:id>/supervisors', supervisors_router)
]