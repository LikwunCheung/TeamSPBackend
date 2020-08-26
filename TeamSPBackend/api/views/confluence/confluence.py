from atlassian import Confluence
import json
import requests
from requests.auth import HTTPBasicAuth

from django.http import HttpResponse

from TeamSPBackend.common.utils import init_http_response
from TeamSPBackend.common.choices import RespCode


def logIntoConfluence():
    """Temporary solution for Confluence login"""
    username = 'yho4'
    password = 'sorry team, I\'m not exposing my password. Gotta wait till I\
    figure out how to retrieve logged-in user details first!'
    confluence = Confluence(
        url='https://confluence.cis.unimelb.edu.au:8443/',
        username=username,
        password=password
    )
    return confluence


def getSpace(request, space_key):
    """Get a Confluence Space
    Method: Get
    Request: space_key
    """
    try:
        print('session looks like ' + str(request.session.items()))
        confluence = logIntoConfluence()
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
    Method: Get
    Request: space
    """
    try:
        confluence = logIntoConfluence()
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
    Method: Get
    """
    try:
        confluence = logIntoConfluence()
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


def getGroupMembers(request, group_name):
    """Get all the members under 'group_name' of the Confluence Space
    Method: Get
    Request: group_name
    """
    try:
        confluence = logIntoConfluence()
        conf_resp = confluence.get_group_members(group_name)
        data = []
        for user in conf_resp:
            data.append({
                'type': user['type'],
                'username': user['username'],
                'userKey': user['userKey'],
                'profilePicture': user['profilePicture'],
                'displayName': user['displayName']
            })
        resp = init_http_response(
            RespCode.success.value.key, RespCode.success.value.msg)
        resp['data'] = data
        return HttpResponse(json.dumps(resp), content_type="application/json")
    except:
        resp = {'code': -1, 'msg': 'error'}
        return HttpResponse(json.dumps(resp), content_type="application/json")


def getUserDetails(request, username):
    """Get a specific Confluence Space member's details
    Method: Get
    Request: username
    """
    try:
        confluence = logIntoConfluence()
        conf_resp = confluence.get_user_details_by_username(username)
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
    try:
        confluence = logIntoConfluence()
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
