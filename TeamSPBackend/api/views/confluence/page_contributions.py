from atlassian import Confluence
import json
import requests
from requests.auth import HTTPBasicAuth

from TeamSPBackend.api.views.confluence import confluence


@require_http_methods(['GET'])
def get_all_page_contributions(request, space_key):
    """
    Get all the page contributions made by each team member
    Method: GET
    Request: space_key
    Return: a dictionary of {"username": [list of contributed page_ids]}
    """
    user = request.session.get('user')
    username = user['atl_username']
    password = user['atl_password']
    try:
        conf = confluence.log_into_confluence(username, password)

        # Get all page ids
        offset = 0
        interval = 100
        page_id_list = []
        response = conf.get_all_pages_from_space(
            space_key, start=offset, limit=interval)
        while (response):
            page_id_list += [page['id'] for page in response]
            offset += interval
            response = conf.get_all_pages_from_space(
                space_key, start=offset, limit=interval)

        for page_id in page_id_list:
            domain = "https://confluence.cis.unimelb.edu.au"
            port = "8443"
            url = f"{domain}:{port}/rest/api/content/{page_id}/history"
            parameters = {"expand": "contributors.publishers.users"}
            conf_resp = requests.get(
                url, params=parameters, auth=HTTPBasicAuth(username, password)).json()
