from slack import WebClient
from TeamSPBackend.api.views.slack.settings import SLACK_CLIENT_ID
from django.views.decorators.http import require_http_methods
from TeamSPBackend.common.utils import check_user_login, make_json_response, init_http_response, check_body
from TeamSPBackend.common.choices import RespCode, Roles
from django.http import HttpResponse, HttpResponseNotAllowed
import json
from TeamSPBackend.team.models import Team
from django.db.models import ObjectDoesNotExist
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

# def channel_exists():
#     token = SLACK_BOT_USER_TOKEN
#     client = WebClient(token=token)
#
#     # grab a list of all the channels in a workspace
#     clist = client.conversations_list()
#     exists = False
#     for k in clist["channels"]:
#         # look for the channel in the list of existing channels
#         if k['name'] == 'the-welcome-channel':
#             exists = True
#         break
#     if exists == False:
#         # create the channel since it doesn't exist
#         # create_channel()


def get_team_data(request, team_id: int):
    print("call slack api")
    try:
        team = Team.objects.get(team_id=team_id)
    except ObjectDoesNotExist:
        resp = init_http_response(RespCode.invalid_op.value.key, RespCode.invalid_op.value.msg)
        resp['team'] = "Invalid team_id"
        return HttpResponse(json.dumps(resp), content_type="application/json")
    # retrieve token by team_id from our database
    token = team.slack_oauth_token
    print(token)
    client = WebClient(token=token)
    # grab a list of all the channels in a workspace
    clist = client.conversations_list()
    channels = []
    for c in clist['channels']:
        channels.append([c['id'], c['name']])
    print(channels)
    for c in channels:
        print(c[0])
        # TODO: Retrieve all messages with start date and end date specified
        chistory = client.conversations_history(channel=c[0])
        print(chistory)
    print(clist)
    resp = init_http_response(RespCode.success.value.key, RespCode.success.value.msg)
    return HttpResponse(json.dumps(resp), content_type="application/json")
