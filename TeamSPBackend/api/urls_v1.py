# -*- coding: utf-8 -*-

from django.urls import path

from TeamSPBackend.api.views import team
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
    path('subject/<int:id>/update', update_subject),
    path('subject/<int:id>/delete', delete_subject),
    path('subject/<int:id>', subject_router),
    path('subject', subject_router),
    
    # Team Related API
    # path('subject/project/team', team.createTeam),
    path('subject/<int:sid>/team', team.create_team),
    # path('subject/project/teamMember', team.team_member),
    path('subject/<int:sid>/team/<int:tid>/teamMember', team.team_member),
    # path('subject/project/getTeam', team.getTeams)
    path('subject/<int:sid>/team/<int:tid>', team.get_teams)
]
