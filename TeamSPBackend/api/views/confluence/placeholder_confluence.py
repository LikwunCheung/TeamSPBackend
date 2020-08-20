from atlassian import Confluence

import json

from django.http import HttpResponse

# TEMPORARY! (Need to access logged in user for actual implementation)
confluence = Confluence(
    url='https://confluence.cis.unimelb.edu.au:8443/',
    username='yho4',
    password=''
)


def getSpace(request):
    """Get a Confluence Space
    Method: Get
    Request:
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
        body = {
            'id': conf_resp['id'],
            'key': conf_resp['key'],
            'name': conf_resp['name'],
            'homepage': {
                'id': conf_homepage['id'],
                'key': conf_homepage['key'],
                'name': conf_homepage['name']
            }
        }
        return HttpResponse(json.dumps(body), content_type="application/json")
    except:
        resp = {'code': -1, 'msg': 'error'}
        return HttpResponse(json.dumps(resp), content_type="application/json")

    # Get all pages

    # Get Page Content by ID (HTML) (lower prio for now)

    # Get group members

    # Get User details

    # Get page history

    # Get page history and its contributors

    # Get page by label
