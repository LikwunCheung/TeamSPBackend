
import logging
from copy import deepcopy

from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from django.db.models import ObjectDoesNotExist

from slack import WebClient
from TeamSPBackend.team.models import TeamConfiguration, Team, Student
from TeamSPBackend.slack.models import SlackTeam, SlackMember
from TeamSPBackend.common.config import MESSAGES_PER_PAGE
from TeamSPBackend.common.utils import make_json_response, check_user_login, mills_timestamp, init_http_response_my_enum
from TeamSPBackend.common.choices import RespCode

logger = logging.getLogger('django')


def get_all_channels(client):

    # grab a list of all the channels in a workspace
    channel_list = client.conversations_list()
    channels = list()
    for c in channel_list['channels']:
        channels.append(dict(
            id=c['id'],
            name=c['name'],
        ))
    return channels


def get_all_users(client):

    user_list = client.users_list()
    users = dict()
    user_email = dict()
    for u in user_list['members']:
        if 'email' not in u['profile']:
            continue
        users[u['id']] = u['real_name']
        user_email[u['id']] = u['profile']['email']

    return users, user_email


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
    sprint_num = int(sprint_num) if sprint_num is not None else -1
    logger.info('sprint_num: {}'.format(sprint_num))

    sprint_start = None
    sprint_end = None
    if sprint_num >= 0:
        parameter_start = 'sprint_start_{}'.format(sprint_num)
        parameter_end = 'sprint_end_{}'.format(sprint_num)
        sprint_start = team.__getattribute__(parameter_start)
        sprint_end = team.__getattribute__(parameter_end)
        logger.info('sprint start {} end {}'.format(sprint_start, sprint_end))

    result = dict()
    temp_result = dict()
    total_number = 0
    if SlackTeam.objects.filter(team_id=team_id, sprint_num=sprint_num).exists():
        records = SlackTeam.objects.filter(team_id=team_id, sprint_num=sprint_num).order_by('time')
        start_time = records[0].time / 1000

        if sprint_end and start_time > sprint_end:
            for record in records:
                result[record.channel_name] = record.message_num
                total_number += record.message_num
            result['total_number'] = total_number
            if sprint_start:
                result['sprint_start'] = sprint_start * 1000
            if sprint_end:
                result['sprint_end'] = sprint_end * 1000
            logger.info('result: {}'.format(result))
            resp = init_http_response_my_enum(RespCode.success, data=result)
            return make_json_response(resp=resp)

        else:
            # call Slack api to get all channel messages in a specific sprint
            for channel in channels:
                messages = get_channel_messages(client, channel['id'], start_time, sprint_end)
                temp_result[channel['name']] = len(messages)
            for record in records:
                record.message_num += temp_result[record.channel_name]
                temp_result.pop(record.channel_name)
                result[record.channel_name] = record.message_num
                total_number += result[record.channel_name]
                record.time = mills_timestamp()
                record.save()

            # save new created channels
            logger.info('temp result: {}'.format(temp_result))
            for (channel, num) in temp_result.items():
                print(channel, num)
                result[channel] = num
                total_number += num
                slack_team = SlackTeam(team_id=team_id, channel_name=channel, message_num=num, sprint_num=sprint_num,
                                       time=mills_timestamp())
                slack_team.save()
            result["total_number"] = total_number
            if sprint_start:
                result['sprint_start'] = sprint_start * 1000
            if sprint_end:
                result['sprint_end'] = sprint_end * 1000
            logger.info('result: {}'.format(result))
            resp = init_http_response_my_enum(RespCode.success, data=result)
            return make_json_response(resp=resp)
    else:
        # call Slack api to get all channel messages in a specific sprint
        for channel in channels:
            messages = get_channel_messages(client, channel['id'], sprint_start, sprint_end)

            logger.info("{}: {}".format(channel['name'], len(messages)))
            result[channel['name']] = len(messages)
            total_number += len(messages)
            slack_team = SlackTeam(team_id=team_id, channel_name=channel['name'], message_num=result[channel['name']],
                                   sprint_num=sprint_num, time=mills_timestamp())
            slack_team.save()
        result['total_number'] = total_number
        if sprint_start:
            result['sprint_start'] = sprint_start * 1000
        if sprint_end:
            result['sprint_end'] = sprint_end * 1000

        logger.info('result: {}'.format(result))
        resp = init_http_response_my_enum(RespCode.success, data=result)
        return make_json_response(resp=resp)


@check_user_login()
def get_all_member_data(request, *args, **kwargs):

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
    users, user_email = get_all_users(client)
    email_id = dict()
    for uid in user_email:
        email_id[user_email[uid]] = uid

    students = Student.objects.filter(email__in=user_email.values()).only('email', 'student_id')
    student_emails = dict()
    for student in students:
        student_emails[student.email] = dict(
            student_id=student.student_id,
        )

    for email in email_id.keys():
        if email in student_emails:
            student_emails[email]['id'] = email_id[email]
            student_emails[email]['name'] = users[email_id[email]]

    # get sprint number from request
    sprint_num = request.GET.get("sprint_num", None)
    sprint_num = int(sprint_num) if sprint_num is not None else -1
    logger.info('sprint_num: {}'.format(sprint_num))

    sprint_start = None
    sprint_end = None
    if sprint_num >= 0:
        parameter_start = 'sprint_start_{}'.format(sprint_num)
        parameter_end = 'sprint_end_{}'.format(sprint_num)
        sprint_start = team.__getattribute__(parameter_start)
        sprint_end = team.__getattribute__(parameter_end)
        logger.info('sprint start {} end {}'.format(sprint_start, sprint_end))

    result = dict()
    for key in student_emails:
        result[student_emails[key]['student_id']] = dict(
            total_number=0,
            name=student_emails[key]['name'],
            channel=dict()
        )
        for channel in channels:
            result[student_emails[key]['student_id']]['channel'][channel['name']] = 0

    total_number = 0
    temp_result = deepcopy(result)

    if SlackMember.objects.filter(team_id=team_id, sprint_num=sprint_num).exists():
        records = SlackMember.objects.filter(team_id=team_id, sprint_num=sprint_num).order_by('time')
        start_time = records[0].time / 1000

        if sprint_end and start_time > sprint_end:
            for record in records:
                result[record.student_id]['total_number'] += record.message_num
                result[record.student_id]['channel'][record.channel_name] = record.message_num
                total_number += record.message_num
            result['total_number'] = total_number
            if sprint_start:
                result['sprint_start'] = sprint_start * 1000
            if sprint_end:
                result['sprint_end'] = sprint_end * 1000
            logger.info('result: {}'.format(result))
            resp = init_http_response_my_enum(RespCode.success, data=result)
            return make_json_response(resp=resp)
        else:
            for channel in channels:
                messages = get_channel_messages(client, channel['id'], start_time, sprint_end)
                for message in messages:
                    if message['user'] not in user_email:
                        continue
                    email = user_email[message['user']]
                    if email not in student_emails:
                        continue
                    student = temp_result[student_emails[email]['student_id']]
                    student['total_number'] += 1
                    student['channel'][channel['name']] += 1
                    total_number += 1

            for record in records:
                record.message_num += temp_result[record.student_id]['channel'][record.channel_name]
                temp_result[record.student_id]['channel'].pop(record.channel_name)
                result[record.student_id]['channel'][record.channel_name] = record.message_num
                result[record.student_id]['total_number'] += record.message_num
                total_number += record.message_num
                record.time = mills_timestamp()
                record.save()

            # save new created channels
            logger.info('temp result: {}'.format(temp_result))
            for student_id in temp_result:
                for k, v in temp_result[student_id]['channel'].items():
                    result[student_id]['channel'][k] = v
                    result[student_id]['total_number'] += v
                    total_number += v
                    slack_member = SlackMember(team_id=team_id, student_id=student_id, channel_name=k, message_num=v,
                                               sprint_num=sprint_num, time=mills_timestamp())
                    slack_member.save()
            result["total_number"] = total_number
            if sprint_start:
                result['sprint_start'] = sprint_start * 1000
            if sprint_end:
                result['sprint_end'] = sprint_end * 1000
            logger.info('result: {}'.format(result))
            resp = init_http_response_my_enum(RespCode.success, data=result)
            return make_json_response(resp=resp)
    else:
        for channel in channels:
            messages = get_channel_messages(client, channel['id'], sprint_start, sprint_end)
            for message in messages:
                if message['user'] not in user_email:
                    continue
                email = user_email[message['user']]
                if email not in student_emails:
                    continue
                student = result[student_emails[email]['student_id']]
                student['total_number'] += 1
                student['channel'][channel['name']] += 1
                total_number += 1

            for student_id in result:
                student = result[student_id]
                slack_member = SlackMember(team_id=team_id, student_id=student_id, channel_name=channel['name'],
                                           message_num=student['channel'][channel['name']], sprint_num=sprint_num,
                                           time=mills_timestamp())
                slack_member.save()

    result['total_number'] = total_number
    if sprint_start:
        result['sprint_start'] = sprint_start * 1000
    if sprint_end:
        result['sprint_end'] = sprint_end * 1000
    logger.info('result: {}'.format(result))
    resp = init_http_response_my_enum(RespCode.success, data=result)
    return make_json_response(resp=resp)


@check_user_login()
def get_member_data(request, *args, **kwargs):

    team_id = kwargs['team_id']
    student_id = int(kwargs['student_id'])

    try:
        team = Team.objects.get(team_id=team_id)
    except ObjectDoesNotExist as e:
        resp = init_http_response_my_enum(RespCode.invalid_parameter)
        return make_json_response(resp=resp)

    client = check_oauth(team_id)
    if not client:
        resp = init_http_response_my_enum(RespCode.invalid_op)
        return make_json_response(resp=resp)
    elif isinstance(client, HttpResponse):
        return client

    channels = get_all_channels(client)
    users, user_email = get_all_users(client)
    email_id = dict()
    for uid in user_email:
        email_id[user_email[uid]] = uid

    student = Student.objects.get(student_id=student_id).only('email', 'student_id')
    student_uid = email_id[student.email]
    student_info = dict(
        email=student.email,
        id=student_uid,
        name=users[email_id[student.email]],
    )

    # get sprint number from request
    sprint_num = request.GET.get("sprint_num", None)
    sprint_num = int(sprint_num) if sprint_num is not None else -1
    logger.info('sprint_num: {}'.format(sprint_num))

    sprint_start = None
    sprint_end = None
    if sprint_num >= 0:
        parameter_start = 'sprint_start_{}'.format(sprint_num)
        parameter_end = 'sprint_end_{}'.format(sprint_num)
        sprint_start = team.__getattribute__(parameter_start)
        sprint_end = team.__getattribute__(parameter_end)
        logger.info('sprint start {} end {}'.format(sprint_start, sprint_end))

    result = dict(
        total_number=0,
        name=student_info['name'],
        channel=dict()
    )

    for channel in channels:
        result['channel'][channel['name']] = 0

    temp_result = deepcopy(result)

    if SlackMember.objects.filter(team_id=team_id, student_id=student_id, sprint_num=sprint_num).exists():
        records = SlackMember.objects.filter(team_id=team_id, student_id=student_id, sprint_num=sprint_num).order_by('time')
        start_time = records[0].time / 1000

        if sprint_end and start_time > sprint_end:
            for record in records:
                result['total_number'] += record.message_num
                result['channel'][record.channel_name] = record.message_num
            logger.info('result: {}'.format(result))
            resp = init_http_response_my_enum(RespCode.success, data=result)
            return make_json_response(resp=resp)
        else:
            for channel in channels:
                messages = get_channel_messages(client, channel['id'], start_time, sprint_end)
                for message in messages:
                    if message['user'] != student_info['id']:
                        continue
                    temp_result['total_number'] += 1
                    temp_result['channel'][channel['name']] += 1

            for record in records:
                record.message_num += temp_result['channel'][record.channel_name]
                temp_result['channel'].pop(record.channel_name)
                result['channel'][record.channel_name] = record.message_num
                result['total_number'] += record.message_num
                record.time = mills_timestamp()
                record.save()

            # save new created channels
            logger.info('temp result: {}'.format(temp_result))
            for k, v in temp_result['channel'].items():
                result['channel'][k] = v
                result['total_number'] += v
                slack_member = SlackMember(team_id=team_id, student_id=student_id, channel_name=k, message_num=v,
                                           sprint_num=sprint_num, time=mills_timestamp())
                slack_member.save()
            logger.info('result: {}'.format(result))
            resp = init_http_response_my_enum(RespCode.success, data=result)
            return make_json_response(resp=resp)
    else:
        for channel in channels:
            messages = get_channel_messages(client, channel['id'], sprint_start, sprint_end)
            for message in messages:
                if message['user'] != student_info['id']:
                    continue
                result['total_number'] += 1
                result['channel'][channel['name']] += 1

            for c in result['channel']:
                slack_member = SlackMember(team_id=team_id, student_id=student_id, channel_name=c,
                                           message_num=result['channel'][c], sprint_num=sprint_num,
                                           time=mills_timestamp())
                slack_member.save()

    logger.info('result: {}'.format(result))
    resp = init_http_response_my_enum(RespCode.success, data=result)
    return make_json_response(resp=resp)