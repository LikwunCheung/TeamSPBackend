from atlassian import Confluence
import json
import requests
from requests.auth import HTTPBasicAuth

from TeamSPBackend.common.choices import RespCode
from django.views.decorators.http import require_http_methods
from django.http.response import HttpResponse, HttpResponseRedirect, HttpResponseNotAllowed, HttpResponseBadRequest
from TeamSPBackend.common.utils import make_json_response, init_http_response, check_user_login, check_body, body_extract, mills_timestamp

@require_http_methods(['GET'])
def get_all_groups(request):
    """Get all groups accessable by the logged in user
    Method: GET
    """
    user = request.session.get('user')
    username = user['atl_username']
    password = user['atl_password']
    print(username)
    print(password)
    try:
        confluence = log_into_confluence(username, password)
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

@require_http_methods(['GET'])
def get_space(request, space_key):
    """Get a Confluence Space
    Method: GET
    Request: space_key
    """
    user = request.session.get('user')
    username = user['atl_username']
    password = user['atl_password']
    try:
        print('session looks like ' + str(request.session.items()))
        confluence = log_into_confluence(username, password)
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

@require_http_methods(['GET'])
def get_pages_of_space(request, space_key):
    """Get all the pages under the Confluence Space
    Method: GET
    Request: space
    """
    user = request.session.get('user')
    username = user['atl_username']
    password = user['atl_password']
    try:
        confluence = log_into_confluence(username, password)
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

@require_http_methods(['GET'])
def search_team(request, keyword):
    user = request.session.get('user')
    username = user['atl_username']
    password = user['atl_password']
    try:
        confluence = log_into_confluence(username, password)
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

@require_http_methods(['GET'])
def get_group_members(request, group):
    
    """Get all the members under 'group_name' of the Confluence Space
    Method: GET
    Request: group_name
    """
    try:
        user = request.session.get('user')
        username = user['atl_username']
        password = user['atl_password']
        group_name = group
        confluence = log_into_confluence(username, password)
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

@require_http_methods(['GET'])
def get_user_details(request, member):
    """Get a specific Confluence Space member's details
    Method: POST
    Request: member's username
    """
    user = request.session.get('user')
    username = user['atl_username']
    password = user['atl_password']
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

@require_http_methods(['GET'])
def get_subject_supervisors(request, subjectcode, year):

    user = request.session.get('user')
    username = user['atl_username']
    password = user['atl_password']
    try:
        confluence = log_into_confluence(username, password)
        conf_resp = confluence.get_all_groups()
        supervisors = []
        data = []
        for group in conf_resp:
            if "staff" in group['name'] and year in group['name'] and subjectcode in group['name']:
                supervisors = confluence.get_group_members(group['name'])

        for each in supervisors:
            data.append({
                # 'type': user['type'],
                # 'userKey': user['userKey'],
                # 'profilePicture': user['profilePicture'],
                'name': each['displayName'],
                'email': each['username']
            })        
        resp = init_http_response(
            RespCode.success.value.key, RespCode.success.value.msg)
        resp['data'] = data
        return HttpResponse(json.dumps(resp), content_type="application/json")
    except:
        resp = {'code': -1, 'msg': 'error'}
        return HttpResponse(json.dumps(resp), content_type="application/json")

@require_http_methods(['GET'])
def get_page_contributors(request, *args, **kwargs):
    """Get a Confluence page's contributors
    Method: Get
    Request: page_id
    """
    user = request.session.get('user')
    username = user['atl_username']
    password = user['atl_password']
    try:
        confluence = log_into_confluence(username, password)
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

def log_into_confluence(username, password):
    confluence = Confluence(
        url='https://confluence.cis.unimelb.edu.au:8443/',
        username=username,
        password=password
    )
    return confluence
