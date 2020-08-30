from atlassian import Confluence
import json
import requests
from requests.auth import HTTPBasicAuth

from django.http import HttpResponse

from TeamSPBackend.common.utils import init_http_response
from TeamSPBackend.common.choices import RespCode
from django.views.decorators.http import require_http_methods

def logIntoConfluence(username, password):
    confluence = Confluence(
        url='https://confluence.cis.unimelb.edu.au:8443/',
        username=username,
        password=password
    )
    return confluence

@require_http_methods(['POST'])
def getSpace(request, space_key):
    """Get a Confluence Space
    Method: POST
    Request: space_key
    """
    username = request.POST.get('username', '')
    password = request.POST.get('password', '') 
    try:
        print('session looks like ' + str(request.session.items()))
        confluence = logIntoConfluence(username, password)
        conf_resp = confluence.get_space(
            space_key, expand='homepage')
        conf_homepage = conf_resp['homepage']
        data = {
            'id': conf_resp['id'],
            'key': conf_resp['key'],
            'name': conf_resp['name'],
            'homepage': {
                'id': conf_homepage['id'],
                'type': conf_homepage['type'],
                'title': conf_homepage['title'],

            }
        }
        resp = init_http_response(
            RespCode.success.value.key, RespCode.success.value.msg)
        resp['data'] = data
        return HttpResponse(json.dumps(resp), content_type="application/json")
    except:
        resp = {'code': -1, 'msg': 'error'}
        return HttpResponse(json.dumps(resp), content_type="application/json")


def getPagesOfSpace(request, space_key):
    """Get all the pages under the Confluence Space
    Method: POST
    Request: space
    """
    username = request.POST.get('username', '')
    password = request.POST.get('password', '') 
    try:
        confluence = logIntoConfluence(username, password)
        conf_resp = confluence.get_all_pages_from_space(space_key)
        data = []
        for page in conf_resp:
            data.append({
                'id': page['id'],
                'type': page['type'],
                'title': page['title']
            })
        resp = init_http_response(
            RespCode.success.value.key, RespCode.success.value.msg)
        resp['data'] = data
        return HttpResponse(json.dumps(resp), content_type="application/json")
    except:
        resp = {'code': -1, 'msg': 'error'}
        return HttpResponse(json.dumps(resp), content_type="application/json")

    # Get Page Content by ID (HTML) (lower prio for now)


def getAllGroups(request):
    """Get all groups accessable by the logged in user
    Method: POST
    """
    username = request.POST.get('username', '')
    password = request.POST.get('password', '') 
    try:
        confluence = logIntoConfluence(username, password)
        conf_resp = confluence.get_all_groups()
        data = []
        for group in conf_resp:
            data.append({
                'type': group['type'],
                'name': group['name']
            })
        resp = init_http_response(
            RespCode.success.value.key, RespCode.success.value.msg)
        resp['data'] = data
        return HttpResponse(json.dumps(resp), content_type="application/json")
    except:
        resp = {'code': -1, 'msg': 'error'}
        return HttpResponse(json.dumps(resp), content_type="application/json")

def searchTeam(request, keyword):
    username = request.POST.get('username', '')
    password = request.POST.get('password', '') 
    try:
        confluence = logIntoConfluence(username, password)
        conf_resp = confluence.get_all_groups()
        data = []
        result = []
        for group in conf_resp:
            data.append({
                'type': group['type'],
                'name': group['name']
            })
        for element in data:
            if keyword.lower() in element['name'].lower():
                result.append({
                    'name': element['name']
                })
        resp = init_http_response(
        RespCode.success.value.key, RespCode.success.value.msg)
        resp['data'] = result
        return HttpResponse(json.dumps(resp), content_type="application/json")
    except:
        resp = {'code': -1, 'msg': 'error'}
        return HttpResponse(json.dumps(resp), content_type="application/json")

@require_http_methods(['POST'])
def getGroupMembers(request):
    
    """Get all the members under 'group_name' of the Confluence Space
    Method: POST
    Request: group_name
    """
    try:
        print(request.POST)
        username = request.POST.get('username')
        print(username)
        print("~~~~~~~~~~")
        password = request.POST.get('password', '')
        group_name = request.POST.get('group_name', '')
        print(username)
        confluence = logIntoConfluence(username, password)
        conf_resp = confluence.get_group_members(group_name)
        data = []
        for user in conf_resp:
            data.append({
                # 'type': user['type'],
                # 'userKey': user['userKey'],
                # 'profilePicture': user['profilePicture'],
                'name': user['displayName'],
                'email': user['username'] + "@student.unimelb.edu.au"
            })
        resp = init_http_response(
            RespCode.success.value.key, RespCode.success.value.msg)
        resp['data'] = data
        return HttpResponse(json.dumps(resp), content_type="application/json")
    except:
        resp = {'code': -1, 'msg': 'error'}
        return HttpResponse(json.dumps(resp), content_type="application/json")


def getUserDetails(request, member):
    """Get a specific Confluence Space member's details
    Method: POST
    Request: member's username
    """
    username = request.POST.get('username', '')
    password = request.POST.get('password', '') 
    try:
        confluence = logIntoConfluence(username, password)
        conf_resp = confluence.get_user_details_by_username(member)
        data = {
            'type': conf_resp['type'],
            'username': conf_resp['username'],
            'userKey': conf_resp['userKey'],
            'profilePicture': conf_resp['profilePicture'],
            'displayName': conf_resp['displayName']
        }
        resp = init_http_response(
            RespCode.success.value.key, RespCode.success.value.msg)
        resp['data'] = data
        return HttpResponse(json.dumps(resp), content_type="application/json")
    except:
        resp = {'code': -1, 'msg': 'error'}
        return HttpResponse(json.dumps(resp), content_type="application/json")


def getPageContributors(request, *args, **kwargs):
    """Get a Confluence page's contributors
    Method: Get
    Request: page_id
    """
    username = request.POST.get('username', '')
    password = request.POST.get('password', '') 
    try:
        confluence = logIntoConfluence(username, password)
        page_id = kwargs['page_id']
        # Todo: change these to configurable inputs
        domain = "https://confluence.cis.unimelb.edu.au"
        port = "8443"
        url = f"{domain}:{port}/rest/api/content/{page_id}/history"
        parameters = {"expand": "contributors.publishers.users"}
        conf_resp = requests.get(
            url, params=parameters, auth=HTTPBasicAuth('yho4', 'mil1maci')).json()
        data = {
            "createdBy": conf_resp["createdBy"],
            "createdDate": conf_resp["createdDate"],
            "contributors": conf_resp["contributors"]
        }
        resp = init_http_response(
            RespCode.success.value.key, RespCode.success.value.msg)
        resp['data'] = data
        return HttpResponse(json.dumps(resp), content_type="application/json")
    except:
        resp = {'code': -1, 'msg': 'error'}
        return HttpResponse(json.dumps(resp), content_type="application/json")

    # Get page by label
