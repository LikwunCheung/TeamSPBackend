# -*- coding: utf-8 -*-

from django.urls import path
from .views.invitation import invitation_router
from .views.subject import *
urlpatterns = [
    # Invitation Related API
    path('subject/<int:id>/invite', invitation_router),
    # Subject Related API
    path('subject/add', addSubject),
    path('subject/<int:id>/update', updateSubject),
    path('subject/<int:id>/delete', deleteSubjects),
    path('subject/<int:id>/get', getSubject)
]