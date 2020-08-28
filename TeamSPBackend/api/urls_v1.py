# -*- coding: utf-8 -*-

from django.urls import path

from TeamSPBackend.api.views import team
from TeamSPBackend.api.views.confluence import confluence
from .views.invitation import invitation_router
from .views.account import account_router, login, logout, update_account, delete, invite_accept
from .views.subject import subject_router, update_subject, delete_subject

urlpatterns = [
    # Invitation Related API
    path('invite', invitation_router),

    # Account Related API
    path('account/login', login),
    path('account/logout', logout),
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
    path('subject/project/team', team.createTeam),
    path('subject/project/teammember', team.team_member),
    path('subject/project/getteam', team.getTeams),

    # Confluence Related API
    path('confluence/spaces/<space_key>', confluence.getSpace),
    path('confluence/spaces/<space_key>/pages', confluence.getPagesOfSpace),
    path('confluence/spaces/<space_key>/pages/<int:page_id>',
         confluence.getPageContributors),
    path('confluence/groups', confluence.getAllGroups),
    path('confluence/groups/<group_name>/members', confluence.getGroupMembers),
    path('confluence/users/<username>', confluence.getUserDetails),
]
