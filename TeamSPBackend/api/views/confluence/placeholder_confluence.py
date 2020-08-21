from atlassian import Confluence

import json
import requests
from requests.auth import HttpBasicAuth

from django.http import HttpResponse

# TEMPORARY! (Need to access logged in user for actual implementation)
username = 'yho4'
password = 'mil1maci'
confluence = Confluence(
    url='https://confluence.cis.unimelb.edu.au:8443/',
    username=username,
    password=password
)


def getSpace(request):
    """Get a Confluence Space
    Method: Get
    Request: space_key
    """
    try:
        space_key = request.GET.get('space_key')
        conf_resp = confluence.get_space(
            space_key, expand='description.plain,homepage')
        # Retrieve
        # - id
        # - key
        # - name
        # - homepage: id, type, title
        conf_homepage = conf_resp['homepage']
        resp = {
            'id': conf_resp['id'],
            'key': conf_resp['key'],
            'name': conf_resp['name'],
            'homepage': {
                'id': conf_homepage['id'],
                'key': conf_homepage['key'],
                'name': conf_homepage['name']
            }
        }
        return HttpResponse(json.dumps(resp), content_type="application/json")
    except:
        resp = {'code': -1, 'msg': 'error'}
        return HttpResponse(json.dumps(resp), content_type="application/json")


def getPagesOfSpace(request):
    """Get all the pages under the Confluence Space
    Method: Get
    Request: space
    """
    try:
        space = request.GET.get('space')
        conf_resp = confluence.get_all_pages_from_space(space)
        resp = []
        for page in conf_resp:
            resp.append({
                'id': page['id'],
                'type': page['type'],
                'title': page['title']
            })
        return HttpResponse(json.dump(resp), content_type="application/json")
    except:
        resp = {'code': -1, 'msg': 'error'}
        return HttpResponse(json.dump(resp), content_type="application/json")

    # Get Page Content by ID (HTML) (lower prio for now)


def getGroupMembers(request):
    """Get all the members under 'group_name' of the Confluence Space
    Method: Get
    Request: group_name
    """
    try:
        group_name = request.GET.get('group_name')
        conf_resp = confluence.get_group_members(group_name)
        resp = []
        for user in conf_resp:
            resp.append({
                'type': user['type'],
                'username': user['username'],
                'userKey': user['userKey'],
                'profilePicture': user['profilePicture'],
                'displayName': user['displayName']
            })
        return HttpResponse(json.dump(resp), content_type="application/json")
    except:
        resp = {'code': -1, 'msg': 'error'}


def getUserDetails(request):
    """Get a specific Confluence Space member's details
    Method: Get
    Request: username
    """
    try:
        username = request.GET.get('username')
        conf_resp = confluence.get_user_details_by_username(username)
        resp = {
            'type': conf_resp['type'],
            'username': conf_resp['username'],
            'userKey': conf_resp['userKey'],
            'profilePicture': conf_resp['profilePicture'],
            'displayName': conf_resp['displayName']
        }
        return HttpResponse(json.dumps(resp), content_type="application/json")
    except:
        resp = {'code': -1, 'msg': 'error'}
        return HttpResponse(json.dumps(resp), content_type="application/json")


def getPageContributors(request):
    """Get a Confluence page's contributors
    Method: Get
    Request: page_id
    """
    try:
        page_id = request.GET.get('page_id')
        # Todo: change these to configurable inputs
        domain = "https://confluence.cis.unimelb.edu.au"
        port = "8443"
        url = f"{domain}:{port}/rest/api/content/{page_id}/history"
        parameters = {"expand": "contributors.publishers.users"}
        conf_resp = requests.get(
            url, params=parameters, auth=HttpBasicAuth(username, password))
        resp = {
            "createdBy": conf_resp["createdBy"],
            "createdDate": conf_resp["createdDate"],
            "contributors": conf_resp["contributors"]
        }
        return HttpResponse(json.dumps(resp), content_type="application/json")
    except:
        resp = {'code': -1, 'msg': 'error'}
        return HttpResponse(json.dump(resp), content_type="application/json")

    # Get page history and its contributors

    # Get page by label
