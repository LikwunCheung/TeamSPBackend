from slack import WebClient
import time
from django.views.decorators.http import require_http_methods
from TeamSPBackend.common.utils import check_user_login, make_json_response, init_http_response, check_body
from TeamSPBackend.common.choices import RespCode, Roles
from django.http import HttpResponse, HttpResponseNotAllowed
import json
from TeamSPBackend.team.models import Team, Student, TeamConfiguration
from TeamSPBackend.slack.models import SlackTeam, SlackMember
from django.db.models import ObjectDoesNotExist

# Slack Settings
MESSAGES_PER_PAGE = 200


def get_all_channels(client):
    # grab a list of all the channels in a workspace
    clist = client.conversations_list()
    channels = []
    for c in clist['channels']:
        channels.append([c['id'], c['name']])
    return channels


def get_channel_messages(client, channel, oldest, latest):
    response = client.conversations_history(
        channel=channel,
        limit=MESSAGES_PER_PAGE,
        # TODO: Add Sprint Time
        latest=latest,
        oldest=oldest,
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
            latest=latest,
            oldest=oldest,
        )
        assert response["ok"]
        messages = response['messages']
        messages_all = messages_all + messages
    return messages_all


def check_oauth(team_id):
    # retrieve Slack configuration
    try:
        team_configuration = TeamConfiguration.objects.get(team_id=team_id)
    except ObjectDoesNotExist:
        resp = init_http_response(RespCode.invalid_op.value.key, RespCode.invalid_op.value.msg)
        resp['data'] = "Invalid team configuration"
        return HttpResponse(json.dumps(resp), content_type="application/json")
    # retrieve token by team_id from team Slack configuration
    if team_configuration.slack_access:
        token = team_configuration.slack_token
    else:
        resp = init_http_response(RespCode.invalid_op.value.key, RespCode.invalid_op.value.msg)
        resp['data'] = "Need access to Slack workspace"
        return HttpResponse(json.dumps(resp), content_type="application/json")

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


def get_sprint_time(team_id):
    # retrieve sprint time from team table
    try:
        team = Team.objects.get(team_id=team_id)
    except ObjectDoesNotExist:
        resp = init_http_response(RespCode.invalid_op.value.key, RespCode.invalid_op.value.msg)
        resp['data'] = "Invalid team_id"
        return HttpResponse(json.dumps(resp), content_type="application/json")

    # retrieve sprint time from team table
    sprint = [team.sprint_start_0, team.sprint_end_0, team.sprint_start_1, team.sprint_end_1, team.sprint_start_2,
              team.sprint_end_2, team.sprint_start_3, team.sprint_end_3, team.sprint_start_4, team.sprint_end_4]
    return sprint


def get_team_data(request, team_id: int):
    print("call get_team_data api")

    # call Slack api to get all Slack channels before the end of the sprint
    client = check_oauth(team_id)
    channels = get_all_channels(client)
    print(channels)

    # get sprint number from request
    sprint_num = int(request.GET.get("sprint_num"))
    print(sprint_num)

    # get sprint start time and end time
    sprint = get_sprint_time(team_id)
    start_time = sprint[sprint_num * 2]
    end_time = sprint[sprint_num * 2 + 1]
    print(start_time, end_time)

    res = {}
    total_number = 0
    tmp = {}
    if SlackTeam.objects.filter(team_id=team_id, sprint_num=sprint_num).exists():
        results = SlackTeam.objects.filter(team_id=team_id, sprint_num=sprint_num)
        start_time = results[0].time
        if start_time > end_time:
            for r in results:
                res[r.channel_name] = r.message_num
                total_number += r.message_num
            res['total-number'] = total_number
            print(res)
            resp = init_http_response(RespCode.success.value.key, RespCode.success.value.msg)
            resp['data'] = res
            return HttpResponse(json.dumps(resp), content_type="application/json")
        else:
            # call Slack api to get all channel messages in a specific sprint
            for c in channels:
                messages = get_channel_messages(client, c[0], start_time, end_time)
                print(c[1], len(messages))
                tmp[c[1]] = len(messages)
            for r in results:
                r.message_num += tmp[r.channel_name]
                tmp.pop(r.channel_name)
                res[r.channel_name] = r.message_num
                total_number += res[r.channel_name]
                r.time = time.time()
                r.save()
            # save new created channels
            print(tmp)
            for (channel, num) in tmp.items():
                print(channel, num)
                res[channel] = num
                total_number += num
                slack_team = SlackTeam(team_id=team_id, channel_name=channel, message_num=num, sprint_num=sprint_num,
                                       time=time.time())
                slack_team.save()
            res["total-number"] = total_number
            print(res)
            resp = init_http_response(RespCode.success.value.key, RespCode.success.value.msg)
            resp['data'] = res
            return HttpResponse(json.dumps(resp), content_type="application/json")
    else:
        # call Slack api to get all channel messages in a specific sprint
        for c in channels:
            messages = get_channel_messages(client, c[0], start_time, end_time)
            print(c[1], len(messages))
            res[c[1]] = len(messages)
            total_number += len(messages)
            slack_team = SlackTeam(team_id=team_id, channel_name=c[1], message_num=res[c[1]], sprint_num=sprint_num,
                                   time=time.time())
            slack_team.save()
        res["total-number"] = total_number
        print(res)
        resp = init_http_response(RespCode.success.value.key, RespCode.success.value.msg)
        resp['data'] = res
        return HttpResponse(json.dumps(resp), content_type="application/json")
    # retrieve sprint time from team table
    try:
        team = Team.objects.get(team_id=team_id)
    except ObjectDoesNotExist:
        resp = init_http_response(RespCode.invalid_op.value.key, RespCode.invalid_op.value.msg)
        resp['data'] = "Invalid team_id"
        return HttpResponse(json.dumps(resp), content_type="application/json")

    # retrieve sprint time from team table
    sprint = [team.sprint_start_0, team.sprint_end_0, team.sprint_start_1, team.sprint_end_1, team.sprint_start_2,
              team.sprint_end_2, team.sprint_start_3, team.sprint_end_3, team.sprint_start_4, team.sprint_end_4]
    return sprint





def get_member_data(request, team_id: int, student_id: int):
    print("call get_individual_data api")

    # Retrieve student record
    try:
        student = Student.objects.get(student_id=student_id)
    except ObjectDoesNotExist:
        resp = init_http_response(RespCode.invalid_op.value.key, RespCode.invalid_op.value.msg)
        resp['student'] = "Invalid student_id"
        return HttpResponse(json.dumps(resp), content_type="application/json")

    # call Slack api to get all Slack channels
    client = check_oauth(team_id)
    member = client.users_lookupByEmail(email=student.email)
    channels = get_all_channels(client)
    print(channels)

    # get sprint number from request
    sprint_num = int(request.GET.get("sprint_num"))
    print(sprint_num)

    # get sprint start time and end time
    sprint = get_sprint_time(team_id)
    start_time = sprint[sprint_num * 2]
    end_time = sprint[sprint_num * 2 + 1]
    print(start_time, end_time)

    res = {}
    total_number = 0
    tmp = {}
    if SlackMember.objects.filter(student_id=student_id, team_id=team_id, sprint_num=sprint_num).exists():
        results = SlackMember.objects.filter(student_id=student_id, team_id=team_id, sprint_num=sprint_num)
        start_time = results[0].time
        # Ready for retrieving
        if start_time > end_time:
            for r in results:
                res[r.channel_name] = r.message_num
                total_number += r.message_num
            res['total-number'] = total_number
            print(res)
            resp = init_http_response(RespCode.success.value.key, RespCode.success.value.msg)
            resp['data'] = res
            return HttpResponse(json.dumps(resp), content_type="application/json")
        # Need update data
        else:
            # call Slack api to get all channel messages sent by the member during a specific sprint
            for c in channels:
                channel_massage_num = 0
                messages = get_channel_messages(client, c[0], start_time, end_time)
                for m in messages:
                    if m['user'] == member['user']['id']:
                        channel_massage_num += 1
                print(c[1], len(messages))
                tmp[c[1]] = channel_massage_num
            for r in results:
                r.message_num += tmp[r.channel_name]
                tmp.pop(r.channel_name)
                res[r.channel_name] = r.message_num
                total_number += res[r.channel_name]
                r.time = time.time()
                r.save()
            # save new created channels
            print(tmp)
            for (channel, num) in tmp.items():
                print(channel, num)
                res[channel] = num
                total_number += num
                slack_member = SlackMember(student_id=student_id, team_id=team_id, channel_name=channel, message_num=num
                                           , sprint_num=sprint_num, time=time.time())
                slack_member.save()
            res["total-number"] = total_number
            print(res)
            resp = init_http_response(RespCode.success.value.key, RespCode.success.value.msg)
            resp['data'] = res
            return HttpResponse(json.dumps(resp), content_type="application/json")
    else:
        # call Slack api to get all channel messages sent by the student during a specific sprint
        for c in channels:
            channel_massage_num = 0
            messages = get_channel_messages(client, c[0], start_time, end_time)
            for m in messages:
                if m['user'] == member['user']['id']:
                    channel_massage_num += 1
            res[c[1]] = channel_massage_num
            total_number += channel_massage_num
            slack_member = SlackMember(student_id=student_id, team_id=team_id, channel_name=c[1], message_num=res[c[1]],
                                       sprint_num=sprint_num, time=time.time())
            slack_member.save()
        res["total-number"] = total_number
        print(res)
        resp = init_http_response(RespCode.success.value.key, RespCode.success.value.msg)
        resp['data'] = res
        return HttpResponse(json.dumps(resp), content_type="application/json")
