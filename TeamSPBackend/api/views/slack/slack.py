from slack import WebClient
import time
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

MESSAGES_PER_PAGE = 200
START_DATE = 0
END_DATE = 0


@check_user_login
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
    """Example"""

    # # get first page
    # page = 1
    # print("Retrieving page {}".format(page))
    # response = client.conversations_history(
    #     channel=CHANNEL,
    #     limit=MESSAGES_PER_PAGE,
    # )
    # assert response["ok"]
    # messages_all = response['messages']
    #
    # # get additional pages if below max message and if they are any
    # while len(messages_all) + MESSAGES_PER_PAGE <= MAX_MESSAGES and response['has_more']:
    #     page += 1
    #     print("Retrieving page {}".format(page))
    #     time.sleep(1)  # need to wait 1 sec before next call due to rate limits
    #     response = client.conversations_history(
    #         channel=CHANNEL,
    #         limit=MESSAGES_PER_PAGE,
    #         cursor=response['response_metadata']['next_cursor']
    #     )
    #     assert response["ok"]
    #     messages = response['messages']
    #     messages_all = messages_all + messages
    #
    # print(
    #     "Fetched a total of {} messages from channel {}".format(
    #         len(messages_all),
    #         CHANNEL
    #     ))
    for c in clist['channels']:
        channels.append([c['id'], c['name']])
    print(channels)
    res = {}
    total_number = 0
    for c in channels:
        print(c[0])
        # TODO: Retrieve all messages with start date and end date specified
        response = client.conversations_history(
            channel=c[0],
            limit=MESSAGES_PER_PAGE,
        )
        assert response["ok"]
        messages_all = response['messages']
        while response['has_more']:
            response = client.conversations_history(
                channel=c[0],
                limit=MESSAGES_PER_PAGE,
                cursor=response['response_metadata']['next_cursor']
            )
            assert response["ok"]
            messages = response['messages']
            messages_all = messages_all + messages
        print(c[1], len(messages_all))
        res[c[1]] = len(messages_all)
        total_number += len(messages_all)
    res["total-number"] = total_number
    print(res)
    resp = init_http_response(RespCode.success.value.key, RespCode.success.value.msg)
    resp['data'] = res
    return HttpResponse(json.dumps(resp), content_type="application/json")
