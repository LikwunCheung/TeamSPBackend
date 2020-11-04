from atlassian import Confluence
import yaml
import json
import requests
from requests.auth import HTTPBasicAuth
from django.http.response import HttpResponse
from django.views.decorators.http import require_http_methods
from urllib.error import HTTPError

from TeamSPBackend.api.views.confluence import confluence
from TeamSPBackend.common.utils import init_http_response, make_json_response
from TeamSPBackend.common.choices import RespCode


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
    conf = confluence.log_into_confluence(username, password)

    # Read confluence config yaml file
    config_dict = read_confluence_config()
    if config_dict == -1:
        resp = init_http_response(
            RespCode.config_not_found.value.key, RespCode.config_not_found.value.msg)
        return make_json_response(HttpResponse, resp)

    # Build query url
    host = config_dict["common"]["host"]
    port = config_dict["common"]["port"]
    base_path = config_dict["common"]["path"]
    api_path = config_dict["api"]["get-all-page-contributors"]["path"]
    query_expand = config_dict["api"]["get-all-page-contributors"]["query"]["expand"]
    query_limit = config_dict["api"]["get-all-page-contributors"]["query"]["limit"]

    base_url = f"{host}:{port}{base_path}{api_path}?expand={query_expand}&limit={query_limit}"

    # Get list of contributors to a page
    url = base_url.replace("{space_key}", space_key, 1)
    conf_resp = requests.get(
        url, auth=HTTPBasicAuth(username, password)).json()

    # Create a dictionary of team members and the number of contributions made to a confluence space
    member_contributions = {}

    # Loop through every page and store in a dictionary {"page": set of members}
    for page in conf_resp["results"]:
        page_contributors = page["history"]["contributors"]["publishers"]["users"]
        for user in page_contributors:
            if not user["username"] in member_contributions:
                member_contributions[user["username"]] = 0
            member_contributions[user["username"]] += 1

    resp = init_http_response(
        RespCode.success.value.key, RespCode.success.value.msg)
    resp['data'] = member_contributions
    return make_json_response(HttpResponse, resp)


def read_confluence_config():
    """
    Helper function to read confluence config yaml file
    """
    try:
        confluence_config = open(
            "TeamSPBackend/common/config/confluence_config.yml")
        config_dict = yaml.load(confluence_config, Loader=yaml.FullLoader)
        return config_dict

    except FileNotFoundError as e:
        return -1
