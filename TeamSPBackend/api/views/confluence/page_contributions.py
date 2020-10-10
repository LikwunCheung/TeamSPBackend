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
    #  user = request.session.get('user')
    #  username = user['atl_username']
    #  password = user['atl_password']
    username = "yho4"
    password = "mil1maci"
    conf = confluence.log_into_confluence(username, password)

    # Get all page ids
    page_id_list = get_list_of_page_ids(space_key, conf)
    if page_id_list == -1:
        resp = init_http_response(
            RespCode.confluence_api_error.value.key, RespCode.confluence_api_error.value.msg)
        return make_json_response(HttpResponse, resp)

    # Read confluence config yaml file
    config_dict = read_confluence_config()
    if config_dict == -1:
        resp = init_http_response(
            RespCode.config_not_found.value.key, RespCode.config_not_found.value.msg)
        return make_json_response(HttpResponse, resp)

    # Create a dictionary of team members and the number of contributions made to a confluence space
    member_contributions = {}
    # Build query url
    host = config_dict["common"]["host"]
    port = config_dict["common"]["port"]
    base_path = config_dict["common"]["path"]
    api_path = config_dict["api"]["get-page-contributors"]["path"]
    query = config_dict["api"]["get-page-contributors"]["query"]
    url = f"{host}:{port}{base_path}{api_path}?{query}"

    #  page_id = page_id_list[0]
    for page_id in page_id_list:

        # Get list of contributors to a page
        new_url = url.replace("{page_id}", str(page_id), 1)
        conf_resp = requests.get(
            new_url, auth=HTTPBasicAuth(username, password)).json()
        users = conf_resp["contributors"]["publishers"]["users"]
        #  print("users is " + str(len(users)))
        #  print("fuck" + url)

        for user in users:
            if not user["username"] in member_contributions:
                member_contributions[user["username"]] = 0
            member_contributions[user["username"]] += 1

    resp = init_http_response(
        RespCode.success.value.key, RespCode.success.value.msg)
    resp['data'] = member_contributions
    return make_json_response(HttpResponse, resp)


def get_list_of_page_ids(space_key, confluence):
    """
    Helper funcction to retrieve a list of page ids for the space (by space_key)
    """

    try:
        offset = 0
        interval = 100
        page_id_list = []
        response = confluence.get_all_pages_from_space(
            space_key, start=offset, limit=interval)
        while (response):
            page_id_list += [page['id'] for page in response]
            offset += interval
            response = confluence.get_all_pages_from_space(
                space_key, start=offset, limit=interval)
        return page_id_list
    except HTTPError as e:
        return -1


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
