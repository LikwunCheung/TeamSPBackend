# from atlassian import Confluence, Jira
from pprint import pprint
import subprocess
import os
import os.path
import fileinput
import time
import json

from django.http.response import HttpResponse, HttpResponseRedirect, HttpResponseNotAllowed, HttpResponseBadRequest
from TeamSPBackend.api.views import account
from django.views.decorators.http import require_http_methods
from TeamSPBackend.common.utils import check_user_login
from TeamSPBackend.team.models import Team, Student, TeamMember
from atlassian import Jira
from TeamSPBackend.common.utils import make_json_response, init_http_response, check_user_login, check_body, body_extract, mills_timestamp
from TeamSPBackend.common.choices import RespCode

@require_http_methods(['GET'])
def get_jira_CFD(request, team):
    user = request.session.get('user')
    username = user['atl_username']
    password = user['atl_password']
    ana_jira(username, password, team)
    while not os.path.exists('TeamSPBackend/api/views/jira/cfd.png'):
        time.sleep(1)

    if os.path.isfile('TeamSPBackend/api/views/jira/cfd.png'):
        time.sleep(1)
        data = open('TeamSPBackend/api/views/jira/cfd.png','rb').read()
        return HttpResponse(data, content_type="image/png")

@require_http_methods(['GET'])
def get_jira_burn(request, team):
    user = request.session.get('user')
    username = user['atl_username']
    password = user['atl_password']
    ana_jira(username, password, team)
    data = open('TeamSPBackend/api/views/jira/burnup.png','rb').read()
    return HttpResponse(data, content_type="image/png")

@require_http_methods(['GET'])
def get_jira_burn_forecast(request, team):
    user = request.session.get('user')
    username = user['atl_username']
    password = user['atl_password']
    ana_jira(username, password, team)
    data = open('TeamSPBackend/api/views/jira/burnup-forecast.png','rb').read()
    return HttpResponse(data, content_type="image/png")

def ana_jira(username, password, project):
    with open('config.yaml', 'r') as file :
        filedata = file.read()
        filedata = filedata.replace('usernameplace', username)
        filedata = filedata.replace('passwordplace', password)
        filedata = filedata.replace('projectplace', project)
    with open('config.yaml', 'w') as file:
        file.write(filedata)

    stream = os.popen("jira-agile-metrics config.yaml --output-directory TeamSPBackend/api/views/jira")

@require_http_methods(['GET'])
def get_issues_one_student(request, team, student_id):
    user = request.session.get('user')
    username = user['atl_username']
    password = user['atl_password']

    student = Student.objects.get(student_id=student_id)
    student_email = student.email
    student_username = student_email.split('@')[0]

    # ############# for manually test only
    # student_username = 'xinbos'
    # team = 'SWEN90013-2020-SP'
    # #############
    jira = Jira(
    url='https://jira.cis.unimelb.edu.au:8444',
    username=username,
    password=password)

    jql_request_total = 'assignee = assignee_name AND project = project_name'
    jql_request_total = jql_request_total.replace('assignee_name', student_username)
    jql_request_total = jql_request_total.replace('project_name', team)
    print(jql_request_total)
    issues_total = jira.jql(jql_request_total)
    count_issues_total = issues_total['total']

    jql_request_to_do = 'assignee = assignee_name AND project = project_name AND status = "To Do"'
    jql_request_to_do = jql_request_to_do.replace('assignee_name', student_username)
    jql_request_to_do = jql_request_to_do.replace('project_name', team)
    issues_to_do = jira.jql(jql_request_to_do)
    count_issues_to_do = issues_to_do['total']

    jql_request_progress = 'assignee = assignee_name AND project = project_name AND status = "In Progress"'
    jql_request_progress = jql_request_progress.replace('assignee_name', student_username)
    jql_request_progress = jql_request_progress.replace('project_name', team)
    issues_progress = jira.jql(jql_request_progress)
    count_issues_progress = issues_progress['total']

    jql_request_done = 'assignee = assignee_name AND project = project_name AND status = "Done"'
    jql_request_done = jql_request_done.replace('assignee_name', student_username)
    jql_request_done = jql_request_done.replace('project_name', team)
    issues_done = jira.jql(jql_request_done)
    count_issues_done = issues_done['total']

    jql_request_review = 'assignee = assignee_name AND project = project_name AND status = "Review"'
    jql_request_review = jql_request_review.replace('assignee_name', student_username)
    jql_request_review = jql_request_review.replace('project_name', team)
    issues_review = jira.jql(jql_request_review)
    count_issues_review = issues_review['total']

    jql_request_in_review = 'assignee = assignee_name AND project = project_name AND status = "In Review"'
    jql_request_in_review = jql_request_in_review.replace('assignee_name', student_username)
    jql_request_in_review = jql_request_in_review.replace('project_name', team)
    issues_in_review = jira.jql(jql_request_in_review)
    count_issues_in_review = issues_in_review['total']

    data = {
        'student_id': student_id,
        'count_issues_total': count_issues_total,
        'count_issues_to_do': count_issues_to_do,
        'count_issues_progress': count_issues_progress,
        'count_issues_in_review': count_issues_in_review,
        'count_issues_done': count_issues_done,
        'count_issues_review': count_issues_review
    }
    resp = init_http_response(
        RespCode.success.value.key, RespCode.success.value.msg)
    resp['data'] = data
    return HttpResponse(json.dumps(resp), content_type="application/json")

@require_http_methods(['GET'])
def get_total_issues_team(request, team):
    user = request.session.get('user')
    username = user['atl_username']
    password = user['atl_password']

    jira = Jira(
    url='https://jira.cis.unimelb.edu.au:8444',
    username=username,
    password=password)

    jql_request = 'project = project_name'
    jql_request = jql_request.replace('project_name', team)
    issues = jira.jql(jql_request)
    count_issues_total = issues['total']

    jql_request = 'project = project_name AND status = "To Do"'
    jql_request = jql_request.replace('project_name', team)
    issues = jira.jql(jql_request)
    count_issues_to_do = issues['total']

    jql_request = 'project = project_name AND status = "In Review"'
    jql_request = jql_request.replace('project_name', team)
    issues = jira.jql(jql_request)
    count_issues_in_review = issues['total']

    jql_request = 'project = project_name AND status = "Review"'
    jql_request = jql_request.replace('project_name', team)
    issues = jira.jql(jql_request)
    count_issues_review = issues['total']

    jql_request = 'project = project_name AND status = "Done"'
    jql_request = jql_request.replace('project_name', team)
    issues = jira.jql(jql_request)
    count_issues_done = issues['total']

    jql_request = 'project = project_name AND status = "In Progress"'
    jql_request = jql_request.replace('project_name', team)
    issues = jira.jql(jql_request)
    count_issues_progress = issues['total']

    data = {
        'team': team,
        'count_issues_total': count_issues_total,
        'count_issues_to_do': count_issues_to_do,
        'count_issues_progress': count_issues_progress,
        'count_issues_in_review': count_issues_in_review,
        'count_issues_done': count_issues_done,
        'count_issues_review': count_issues_review
    }
    resp = init_http_response(
        RespCode.success.value.key, RespCode.success.value.msg)
    resp['data'] = data
    return HttpResponse(json.dumps(resp), content_type="application/json")

@require_http_methods(['GET'])
def get_comment_count_one_student(request, team, student_id):
    user = request.session.get('user')
    username = user['atl_username']
    password = user['atl_password']

    jira = Jira(
    url='https://jira.cis.unimelb.edu.au:8444',
    username=username,
    password=password)

    student = Student.objects.get(student_id=student_id)
    student_email = student.email
    student_username = student_email.split('@')[0]

    issues = json.dumps(jira.get_all_project_issues(team, fields='comment'))
    count = issues.count(student_username)
    resp = init_http_response(
        RespCode.success.value.key, RespCode.success.value.msg)
    resp['student_id'] = student_id
    resp['username'] = student_username
    resp['comments'] = count/16
    return HttpResponse(json.dumps(resp), content_type="application/json")


@require_http_methods(['GET'])
def get_sprints_dates(request, team):
    user = request.session.get('user')
    username = user['atl_username']
    password = user['atl_password']

    jira = Jira(
        url='https://jira.cis.unimelb.edu.au:8444',
        username=username,
        password=password
    )

    resp = init_http_response(RespCode.success.value.key, RespCode.success.value.msg)

    issues = json.dumps(jira.get_all_project_issues(team, fields='*all'))
    pprint(issues)
    split = issues.split("name=Sprint 1,startDate=", 1)
    split2 = split[1].split("endDate=",1)
    if split[1][:10].startswith('20'):
        resp['sprint_1_start'] = split[1][:10]
    else:
        resp['sprint_1_start'] = "null"
    if split[1][:10].startswith('20'):    
        resp['sprint_1_end'] = split2[1][:10]
    else:
        resp['sprint_1_end'] = "null"

    split = issues.split("name=Sprint 2,startDate=", 1)
    split2 = split[1].split("endDate=",1)
    if split[1][:10].startswith('20'):
        resp['sprint_2_start'] = split[1][:10]
    else:
        resp['sprint_2_start'] = "null"
    if split[1][:10].startswith('20'):    
        resp['sprint_2_end'] = split2[1][:10]
    else:
        resp['sprint_2_end'] = "null"

    split = issues.split("name=Sprint 3,startDate=", 1)
    split2 = split[1].split("endDate=",1)
    if split[1][:10].startswith('20'):
        resp['sprint_3_start'] = split[1][:10]
    else:
        resp['sprint_3_start'] = "null"
    if split[1][:10].startswith('20'):    
        resp['sprint_3_end'] = split2[1][:10]
    else:
        resp['sprint_3_end'] = "null"

    split = issues.split("name=Sprint 4,startDate=", 1)
    split2 = split[1].split("endDate=",1)
    if split[1][:10].startswith('20'):
        resp['sprint_4_start'] = split[1][:10]
    else:
        resp['sprint_4_start'] = "null"
    if split[1][:10].startswith('20'):    
        resp['sprint_4_end'] = split2[1][:10]
    else:
        resp['sprint_4_end'] = "null"
    return HttpResponse(json.dumps(resp), content_type="application/json")


@require_http_methods(['GET'])
def get_issues_per_sprint(request, team):
    user = request.session.get('user')
    username = user['atl_username']
    password = user['atl_password']

    jira = Jira(
    url='https://jira.cis.unimelb.edu.au:8444',
    username=username,
    password=password)


    resp = init_http_response(
        RespCode.success.value.key, RespCode.success.value.msg)
    issues = json.dumps(jira.get_all_project_issues(team, fields='*all'))
    split = issues.split("[id=")
    sprint_ids = []
    for str in split[1:]:
        split2 = str.split(",")
        id = split2[0]
        if id not in sprint_ids:
            sprint_ids.append(id)
    sprint_ids.sort()
    i = 1
    for id in sprint_ids:
        jql_request = 'Sprint = id'
        jql_request = jql_request.replace('id', id)
        issues = jira.jql(jql_request)
        count_issues_total = issues['total']
        resp[i] = count_issues_total
        i += 1
    return HttpResponse(json.dumps(resp), content_type="application/json")
# 2. reviewer

# @require_http_methods(['GET'])
# def get_issues_sprints(request, team):
#     user = request.session.get('user')
#     username = user['atl_username']
#     password = user['atl_password']

#     jira = Jira(
#     url='https://jira.cis.unimelb.edu.au:8444',
#     username=username,
#     password=password)

#     jql_request = 'project = project_name AND status = "In Progress"'
#     jql_request = jql_request.replace('project_name', team)
#     issues = jira.jql(jql_request)
