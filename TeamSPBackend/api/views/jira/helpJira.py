# from atlassian import Confluence, Jira
from pprint import pprint
import subprocess
import os
import os.path
import fileinput
import time

from django.http.response import HttpResponse, HttpResponseRedirect, HttpResponseNotAllowed, HttpResponseBadRequest
from TeamSPBackend.api.views import account
from django.views.decorators.http import require_http_methods
from TeamSPBackend.common.utils import check_user_login


@require_http_methods(['POST'])
def get_jira_CFD(request):
    username = request.POST.get('username', '')
    password = request.POST.get('password', '')
    project = request.POST.get('team', '')
    ana_jira(username, password, project)
    while not os.path.exists('TeamSPBackend/api/views/jira/cfd.png'):
        time.sleep(1)

    if os.path.isfile('TeamSPBackend/api/views/jira/cfd.png'):
        time.sleep(1)
        data = open('TeamSPBackend/api/views/jira/cfd.png','rb').read()
        return HttpResponse(data, content_type="image/png")

def get_jira_burn(request):
    username = request.POST.get('username', '')
    password = request.POST.get('password', '')
    project = request.POST.get('team', '')
    ana_jira(username, password, project)
    data = open('TeamSPBackend/api/views/jira/burnup.png','rb').read()
    return HttpResponse(data, content_type="image/png")

def get_jira_burn_forecast(request):
    username = request.POST.get('username', '')
    password = request.POST.get('password', '')
    project = request.POST.get('team', '')
    ana_jira(username, password, project)
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
    
    # with open('config.yaml', 'r') as file :
    #     filedata = file.read()
    #     filedata = filedata.replace(username, 'usernameplace')
    #     filedata = filedata.replace(password, 'passwordplace')
    #     filedata = filedata.replace(project, 'projectplace')
    # with open('config.yaml', 'w') as file:
    #     file.write(filedata)

# jira = Jira(
#     url='https://jira.cis.unimelb.edu.au:8444',
#     username='xinbos',
#     password='sxb306103.')
# jql_request = 'Sprint = 774'
# issues = jira.jql(jql_request)
# print(issues)
