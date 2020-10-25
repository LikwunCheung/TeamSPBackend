# -*- coding: utf-8 -*-

from django.urls import path

from TeamSPBackend.api.views.confluence import confluence
from TeamSPBackend.api.views.confluence import page_contributions
from TeamSPBackend.api.views.jira import helpJira
from .views.invitation import invitation_router, invite_accept
from .views.account import account_router, login, logout, update_account, delete, atl_login, supervisor_router
from .views.subject import subject_router, update_subject, delete_subject
from .views.team import team_router, get_team_members
from .views.slack1.slack import get_member_data
from .views.slack import get_team_data, get_all_member_data
from .views.git import get_git_commits

urlpatterns = [
    # Invitation Related API
    path('invite', invitation_router),
    path('invite/accept', invite_accept),

    # Account Related API
    path('account/login', login),
    path('account/atlassian/login', atl_login),
    path('account/logout', logout),
    path('account/update', update_account),
    path('account/delete', delete),
    path('account', account_router),

    # Supervisor Related API
    path('supervisor/<int:id>', supervisor_router),
    path('supervisor', supervisor_router),

    # Subject Related API
    path('subject/<int:id>/update', update_subject),
    path('subject/<int:id>/delete', delete_subject),
    path('subject/<int:id>', subject_router),
    path('subject', subject_router),

    # Team Related API
    path('team', team_router),
    path('team/<int:id>', team_router),
    path('team/<int:id>/members', get_team_members),

    # Git Related API
    path('git/commit', get_git_commits),

    # Confluence Related API
    path('confluence/spaces/<space_key>', confluence.get_space),
    path('confluence/spaces/<space_key>/pages', confluence.get_pages_of_space),
    path('confluence/spaces/<space_key>/pages/contributions',
         page_contributions.get_all_page_contributions),
    path('confluence/spaces/<space_key>/pages/<int:page_id>',
         confluence.get_page_contributors),
    path('confluence/groups', confluence.get_all_groups),
    path('confluence/groups/searchteam/<keyword>', confluence.search_team),
    path('confluence/groups/<group>/members', confluence.get_group_members),
    path('confluence/users/<member>', confluence.get_user_details),
    path('subject/<subjectcode>/<year>/supervisors',
         confluence.get_subject_supervisors),

    # Jira Related API
    path('jira/<team>/jiracfd', helpJira.get_jira_CFD),
    path('jira/<team>/jiraburn', helpJira.get_jira_burn),
    path('jira/<team>/jiraburnforecast', helpJira.get_jira_burn_forecast),
    path('jira/<team>/tickets/<student_id>', helpJira.get_issues_one_student),
    path('jira/<team>/tickets', helpJira.get_total_issues_team),
    path('jira/<team>/sprintdates', helpJira.get_sprints_dates),
    path('jira/<team>/issuespersprint', helpJira.get_issues_per_sprint),
    path('jira/<team>/comments/<student_id>', helpJira.get_comment_count_one_student),
  
    # Slack Related API
    # path('slack', slack_router),
    path('slack/<int:id>', get_team_data),
    path('slack/<int:id>/member', get_all_member_data),
    path('slack/<int:team_id>/member/<int:student_id>', get_member_data),
]
    

