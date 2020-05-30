# -*- coding: utf-8 -*-

from django.urls import path
from .views.invitation import invitation_router
from .views.subject import subject_router
from .views import supervisors
urlpatterns = [
    # Invitation Related API
    path('subject/<int:id>/invite', invitation_router),

    # Invitation Related API
    path('subject/<int:id>/supervisors', supervisors.supervisors_router)
    # Add subject
    path('subject/add', supervisors.subject_add)
    # Update subject
    path('subject/update', supervisors.subject_update)
    # Delete subject
    path('subject/delete', supervisors.subject_delete)
    # Get subject
    path('subject/<int:subject_id>', supervisors.subject_get)
]
