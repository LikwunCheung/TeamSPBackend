
import logging

from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from django.db.models import ObjectDoesNotExist

from slack import WebClient
from TeamSPBackend.team.models import TeamConfiguration, Team
from TeamSPBackend.slack.models import SlackTeam, SlackMember
from TeamSPBackend.common.config import MESSAGES_PER_PAGE
from TeamSPBackend.common.utils import make_json_response, check_user_login, mills_timestamp, init_http_response_my_enum
from TeamSPBackend.common.choices import RespCode

logger = logging.getLogger('django')


def get_all_channels(client):

    # grab a list of all the channels in a workspace
    channel_list = client.conversations_list()
    channels = []
    for c in channel_list['channels']:
        channels.append(dict(
            id=c['id'],
            name=c['name'],
        ))
    return channels


def get_channel_messages(client, channel, start_time, end_time):

    parameter = dict(
        channel=channel,
        limit=MESSAGES_PER_PAGE,
    )
    if end_time:
        parameter['latest'] = end_time
    if start_time:
        parameter['oldest'] = start_time

    response = client.conversations_history(**parameter)
    assert response["ok"]
    messages_all = response['messages']

    while response['has_more']:
        # time.sleep(1)  # need to wait 1 sec before next call due to rate limits
        parameter['cursor'] = response['response_metadata']['next_cursor']
        response = client.conversations_history(**parameter)
        assert response["ok"]
        messages = response['messages']
        messages_all = messages_all + messages
    return messages_all


def check_oauth(team_id):

    # retrieve Slack configuration
    try:
        team_configuration = TeamConfiguration.objects.get(team_id=team_id)
    except ObjectDoesNotExist as e:
        resp = init_http_response_my_enum(RespCode.invalid_op)
        resp['message'] = "Invalid team configuration"
        return make_json_response(resp=resp)

    # retrieve token by team_id from team Slack configuration
    if team_configuration.slack_access:
        token = team_configuration.slack_token
        if token:
            slack_client = WebClient(token=token)
            return slack_client
    else:
        resp = init_http_response_my_enum(RespCode.invalid_op)
        resp['message'] = "Need access to Slack workspace"
        return make_json_response(resp=resp)

    # Todo: Oauth v2
    return None
    # print("Need Authorization")
    # resp = init_http_response(RespCode.invalid_op.value.key, RespCode.invalid_op.value.msg)
    # resp['token'] = "Need Authorization"
    # return HttpResponse(json.dumps(resp), content_type="application/json")


@require_http_methods(['GET'])
@check_user_login()
def get_team_data(request, *args, **kwargs):

    team_id = kwargs['id']
    try:
        team = Team.objects.get(team_id=team_id)
    except ObjectDoesNotExist as e:
        resp = init_http_response_my_enum(RespCode.invalid_parameter)
        return make_json_response(resp=resp)

    # call Slack api to get all Slack channels before the end of the sprint
    client = check_oauth(team_id)
    if not client:
        resp = init_http_response_my_enum(RespCode.invalid_op)
        return make_json_response(resp=resp)
    elif isinstance(client, HttpResponse):
        return client

    channels = get_all_channels(client)
    logger.info('channel: {}'.format(channels))

    # get sprint number from request
    sprint_num = request.GET.get("sprint_num", None)
    sprint_num = int(sprint_num) if sprint_num else sprint_num
    logger.info('sprint_num: {}', sprint_num)

    sprint_start = None
    sprint_end = None
    if sprint_num:
        parameter_start = 'sprint_start_{}'.format(sprint_num)
        parameter_end = 'sprint_end_{}'.format(sprint_num)
        sprint_start = team.__getattribute__(parameter_start, None)
        sprint_end = team.__getattribute__(parameter_end, None)
        logger.info('sprint start {} end {}'.format(sprint_start, sprint_end))

    result = dict()
    temp_result = dict()
    total_number = 0
    if SlackTeam.objects.filter(team_id=team_id, sprint_num=sprint_num).exists():
        records = SlackTeam.objects.filter(team_id=team_id, sprint_num=sprint_num).order_by('time')
        start_time = records[0].time

        if sprint_end and start_time > sprint_end:
            for record in records:
                result[record.channel_name] = record.message_num
                total_number += record.message_num
            result['total_number'] = total_number
            logger.info('result: {}', result)
            resp = init_http_response_my_enum(RespCode.success, data=result)
            return make_json_response(resp=resp)

        else:
            # call Slack api to get all channel messages in a specific sprint
            for channel in channels:
                messages = get_channel_messages(client, channel['id'], start_time, sprint_end)
                logger.info(channel['name'], len(messages))
                temp_result[channel['name']] = len(messages)
            for channel in records:
                channel.message_num += temp_result[channel.channel_name]
                temp_result.pop(channel.channel_name)
                result[channel.channel_name] = channel.message_num
                total_number += result[channel.channel_name]
                channel.time = mills_timestamp()
                channel.save()

            # save new created channels
            logger.info('temp result: {}', temp_result)
            for (channel, num) in temp_result.items():
                print(channel, num)
                result[channel] = num
                total_number += num
                slack_team = SlackTeam(team_id=team_id, channel_name=channel, message_num=num, sprint_num=sprint_num,
                                       time=mills_timestamp())
                slack_team.save()
            result["total_number"] = total_number
            logger.info('result: {}', result)
            resp = init_http_response_my_enum(RespCode.success, data=result)
            return make_json_response(resp=resp)
    else:
        # call Slack api to get all channel messages in a specific sprint
        sprint_num = -1 if not sprint_num else sprint_num
        for channel in channels:
            messages = get_channel_messages(client, channel['id'], sprint_start, sprint_end)

            logger.info(channel['name'], len(messages))
            result[channel['name']] = len(messages)
            total_number += len(messages)
            slack_team = SlackTeam(team_id=team_id, channel_name=channel['id'], message_num=result[channel['name']],
                                   sprint_num=sprint_num, time=mills_timestamp())
            slack_team.save()
        result['total_number'] = total_number

        logger.info('result: {}', result)
        resp = init_http_response_my_enum(RespCode.success, data=result)
        return make_json_response(resp=resp)


