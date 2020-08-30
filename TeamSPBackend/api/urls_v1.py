# -*- coding: utf-8 -*-

from django.urls import path

from TeamSPBackend.api.views import team
from TeamSPBackend.api.views.confluence import confluence
from .views.invitation import invitation_router, invite_accept
from .views.account import account_router, login, logout, update_account, delete
from .views.subject import subject_router, update_subject, delete_subject
from .views.team import team_router, get_team_members

from TeamSPBackend.api.views.jira import helpJira
urlpatterns = [
    # Invitation Related API
    path('invite', invitation_router),
    path('invite/accept', invite_accept),

    # Account Related API
    path('account/login', login),
    path('account/logout', logout),
    path('account/update', update_account),
    path('account/delete', delete),
    path('account', account_router),

    # Subject Related API
    path('subject/<int:id>/update', update_subject),
    path('subject/<int:id>/delete', delete_subject),
    path('subject/<int:id>', subject_router),
    path('subject', subject_router),

    # Team Related API
    path('team', team_router),
    path('team/<int:team_id>', team_router),
    path('team/<int:team_id>/members', get_team_members),

    # Confluence Related API
    path('confluence/spaces/<space_key>', confluence.getSpace),
    path('confluence/spaces/<space_key>/pages', confluence.getPagesOfSpace),
    path('confluence/spaces/<space_key>/pages/<int:page_id>',
         confluence.getPageContributors),
    path('confluence/groups', confluence.getAllGroups),
    path('confluence/groups/searchteam/<keyword>', confluence.searchTeam),
    path('confluence/groups/<group>/members', confluence.getGroupMembers),
    path('confluence/users/<username>', confluence.getUserDetails)
    # Jira Related API
    path('subject/project/team/jiracfd', helpJira.getJiraCFD),
    path('subject/project/team/jiraburn', helpJira.getJiraburn),
    path('subject/project/team/jiraburnforecast', helpJira.getJiraburnforecast)

]
