# -*- coding: utf-8 -*-

from django.urls import path

from TeamSPBackend.api.views import team
from TeamSPBackend.api.views.confluence import confluence
from .views.invitation import invitation_router
from .views.account import account_router, atl_login, login, update_account, delete, invite_accept
from .views.subject import subject_router, update_subject, delete_subject
from TeamSPBackend.api.views.jira import helpJira
urlpatterns = [
    # Invitation Related API
    path('subject/<int:id>/invite', invitation_router),

    # Account Related API
    path('account/login', login),
    path('account/atlassian/login', atl_login),
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
    path('confluence/spaces/<space_key>', confluence.get_space),
    path('confluence/spaces/<space_key>/pages', confluence.get_pages_of_space),
    path('confluence/spaces/<space_key>/pages/<int:page_id>',
        confluence.get_page_contributors),
    path('confluence/groups', confluence.get_all_groups),
    path('confluence/groups/searchteam/<keyword>', confluence.search_team),
    path('confluence/groups/<group>/members', confluence.get_group_members),
    path('confluence/users/<member>', confluence.get_user_details),
    path('subject/<subjectcode>/<year>/supervisors', confluence.get_subject_supervisors),
    # Jira Related API
    path('jira/<team>/jiracfd', helpJira.get_jira_CFD),
    path('jira/<team>/jiraburn', helpJira.get_jira_burn),
    path('jira/<team>/jiraburnforecast', helpJira.get_jira_burn_forecast)

]
