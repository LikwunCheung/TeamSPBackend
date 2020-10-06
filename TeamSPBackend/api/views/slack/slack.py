from slack import WebClient
import time
from django.views.decorators.http import require_http_methods
from TeamSPBackend.common.utils import check_user_login, make_json_response, init_http_response, check_body
from TeamSPBackend.common.choices import RespCode, Roles
from django.http import HttpResponse, HttpResponseNotAllowed
import json
from TeamSPBackend.team.models import Team
from TeamSPBackend.account.models import User
from django.db.models import ObjectDoesNotExist

# Slack Settings
SLACK_CLIENT_ID = '965258290579.1356270476084'
MESSAGES_PER_PAGE = 200
START_DATE = 0
END_DATE = 0


# @require_http_methods(['POST', 'GET'])
# @check_user_login
# def slack_router(request, *args):
#     team_id = None
#     for arg in args:
#         if isinstance(arg, dict):
#             team_id = arg.get('team_id', None)
#     if request.method == 'POST':
#         if team_id:
#             return
#     elif request.method == 'GET':
#         if team_id:
#             return


def get_all_channels(client):
    # grab a list of all the channels in a workspace
    clist = client.conversations_list()
    channels = []
    for c in clist['channels']:
        channels.append([c['id'], c['name']])
    return channels


def get_channel_messages(client, channel, latest = 0, oldest = 0):
    response = client.conversations_history(
        channel=channel,
        limit=MESSAGES_PER_PAGE,
        # TODO: Add Sprint Time
        # latest = ,
        # oldest = ,
    )
    assert response["ok"]
    messages_all = response['messages']
    while response['has_more']:
        # time.sleep(1)  # need to wait 1 sec before next call due to rate limits
        response = client.conversations_history(
            channel=channel,
            limit=MESSAGES_PER_PAGE,
            cursor=response['response_metadata']['next_cursor'],
            # TODO: Add Sprint Time
            # latest = ,
            # oldest = ,
        )
        assert response["ok"]
        messages = response['messages']
        messages_all = messages_all + messages
    return messages_all


def check_oauth(team_id):
    try:
        team = Team.objects.get(team_id=team_id)
    except ObjectDoesNotExist:
        resp = init_http_response(RespCode.invalid_op.value.key, RespCode.invalid_op.value.msg)
        resp['team'] = "Invalid team_id"
        return HttpResponse(json.dumps(resp), content_type="application/json")
    # retrieve token by team_id from our database
    token = team.slack_oauth_token
    # create a Slack client using the token
    if token:
        client = WebClient(token=token)
        return client
    else:
        # Todo: Oauth v2
        return None
        # print("Need Authorization")
        # resp = init_http_response(RespCode.invalid_op.value.key, RespCode.invalid_op.value.msg)
        # resp['token'] = "Need Authorization"
        # return HttpResponse(json.dumps(resp), content_type="application/json")


def get_team_data(request, team_id: int):
    print("call get_team_data api")
    client = check_oauth(team_id)
    channels = get_all_channels(client)
    print(channels)
    res = {}
    total_number = 0
    for c in channels:
        messages = get_channel_messages(client, c[0])
        print(c[1], len(messages))
        res[c[1]] = len(messages)
        total_number += len(messages)
    res["total-number"] = total_number
    print(res)
    resp = init_http_response(RespCode.success.value.key, RespCode.success.value.msg)
    resp['data'] = res
    return HttpResponse(json.dumps(resp), content_type="application/json")


def get_member_data(request, team_id: int, user_id: int):
    print("call get_individual_data api")
    try:
        user = User.objects.get(user_id=user_id)
    except ObjectDoesNotExist:
        resp = init_http_response(RespCode.invalid_op.value.key, RespCode.invalid_op.value.msg)
        resp['user'] = "Invalid user_id"
        return HttpResponse(json.dumps(resp), content_type="application/json")
    client = check_oauth(team_id)
    member = client.users_lookupByEmail(email=user.email)
    channels = get_all_channels(client)
    print(channels)
    res = {}
    total_number = 0
    for c in channels:
        messages = get_channel_messages(client, c[0])
        print(c[1], len(messages))
        res[c[1]] = len(messages)
        total_number += len(messages)
    print(member)
