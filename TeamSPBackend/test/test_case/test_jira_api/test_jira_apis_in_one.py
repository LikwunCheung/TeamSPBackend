import unittest   # The test framework
from django.test import TestCase, Client
from django.http import HttpRequest
from TeamSPBackend.api.views.jira import helpJira
from atlassian import Jira
from TeamSPBackend.common.utils import make_json_response, init_http_response, check_user_login, check_body, body_extract, mills_timestamp
import json
from TeamSPBackend.common.choices import RespCode
from pprint import pprint

class Test_issues(TestCase):

    def test_collect_issues_of_a_student(self):        
        jira = Jira(
        url='https://jira.cis.unimelb.edu.au:8444',
        username="xinbos",
        password="sxb306103.")
        student_username = 'xinbos'
        team = 'SWEN90013-2020-SP'
        jql_request_total = 'assignee = xinbos AND project = SWEN90013-2020-SP'
        issues_total = jira.jql(jql_request_total)
        count_issues_total = issues_total['total']

        jql_request_to_do = 'assignee = xinbos AND project = SWEN90013-2020-SP AND status = "To Do"'
        issues_to_do = jira.jql(jql_request_to_do)
        count_issues_to_do = issues_to_do['total']

        jql_request_progress = 'assignee = xinbos AND project = SWEN90013-2020-SP AND status = "In Progress"'
        issues_progress = jira.jql(jql_request_progress)
        count_issues_progress = issues_progress['total']

        jql_request_done = 'assignee = xinbos AND project = SWEN90013-2020-SP AND status = "Done"'
        issues_done = jira.jql(jql_request_done)
        count_issues_done = issues_done['total']

        jql_request_review = 'assignee = xinbos AND project = SWEN90013-2020-SP AND status = "Review"'
        issues_review = jira.jql(jql_request_review)
        count_issues_review = issues_review['total']

        jql_request_in_review = 'assignee = xinbos AND project = SWEN90013-2020-SP AND status = "In Review"'
        issues_in_review = jira.jql(jql_request_in_review)
        count_issues_in_review = issues_in_review['total']

        data = {
            'count_issues_total': count_issues_total,
            'count_issues_to_do': count_issues_to_do,
            'count_issues_progress': count_issues_progress,
            'count_issues_in_review': count_issues_in_review,
            'count_issues_done': count_issues_done,
            'count_issues_review': count_issues_review
        }

        self.assertNotEqual(count_issues_total, 0)
    
    def test_team_issues(self):
        jira = Jira(
        url='https://jira.cis.unimelb.edu.au:8444',
        username="xinbos",
        password="sxb306103.")

        jql_request = 'project = SWEN90013-2020-SP'
        issues = jira.jql(jql_request)
        count_issues_total = issues['total']
        self.assertNotEqual(count_issues_total, 0)

    def test_team_issues(self):
        jira = Jira(
        url='https://jira.cis.unimelb.edu.au:8444',
        username="xinbos",
        password="sxb306103.")

        jql_request = 'project = SWEN90013-2020-SP'
        issues = jira.jql(jql_request)
        count_issues_total = issues['total']
        self.assertNotEqual(count_issues_total, 0)

    def test_comments_by_a_student(self):
        jira = Jira(
        url='https://jira.cis.unimelb.edu.au:8444',
        username="xinbos",
        password="sxb306103.")
        issues = json.dumps(jira.get_all_project_issues('SWEN90013-2020-SP', fields='comment'))
        countXinbo = issues.count('xinbos')/16
        countZach = issues.count('yho4')/16
        self.assertEqual(countXinbo, 0)
        self.assertNotEqual(countZach, 0)

    def test_issues_per_sprint(self):
        jira = Jira(
        url='https://jira.cis.unimelb.edu.au:8444',
        username="xinbos",
        password="sxb306103.")

        resp = init_http_response(
        RespCode.success.value.key, RespCode.success.value.msg)
        issues = json.dumps(jira.get_all_project_issues('SWEN90013-2020-SP', fields='*all'))
        split = issues.split("[id=")
        sprint_ids = []
        for str in split[1:]:
            split2 = str.split(",")
            id = split2[0]
            if id not in sprint_ids:
                sprint_ids.append(id)
        sprint_ids.sort()
        i = 1
        for id in sprint_ids:
            jql_request = 'Sprint = id'
            jql_request = jql_request.replace('id', id)
            issues = jira.jql(jql_request)
            count_issues_total = issues['total']
            resp[i] = count_issues_total
            i += 1

        self.assertNotEqual(resp[1], 0)
        self.assertNotEqual(resp[2], 0)
        self.assertNotEqual(resp[3], 0)

    def test_issues_per_sprint(self):
        jira = Jira(
        url='https://jira.cis.unimelb.edu.au:8444',
        username="xinbos",
        password="sxb306103.")
        resp = init_http_response(RespCode.success.value.key, RespCode.success.value.msg)
        issues = json.dumps(jira.get_all_project_issues('SWEN90013-2020-SP', fields='*all'))
        split = issues.split("name=Sprint 1,startDate=", 1)
        split2 = split[1].split("endDate=",1)
        if split[1][:10].startswith('20'):
            resp['sprint_1_start'] = split[1][:10]
        else:
            resp['sprint_1_start'] = "null"
        if split[1][:10].startswith('20'):    
            resp['sprint_1_end'] = split2[1][:10]
        else:
            resp['sprint_1_end'] = "null"
        self.assertNotEqual(resp['sprint_1_start'], "null")
        self.assertNotEqual(resp['sprint_1_end'], "null")
if __name__ == '__main__':
    unittest.main()
