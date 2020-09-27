# coding:utf-8
import os
import unittest


from HTMLTestRunner import *
from test_case.test_dto import *
from test_case.test_tutorial_2 import *

from TeamSPBackend.test.HTMLTestRunner import HTMLTestRunner

suite = unittest.TestSuite()

report_name = 'Backend_Test_Report'
report_title = "Subject and supervisor tests"
report_des = 'Get + Multiget Subjects and Supervisors'
report_path = './report/' + 'test_subject_view'
report_file = report_path + 'test_get_subject_report_01.html'
if not os.path.exists(report_path):
    os.mkdir(report_path)
else:
    pass
with open(report_file, 'wb') as report:
    suite.addTests(unittest.TestLoader().loadTestsFromName(
        'test_case.test_subject_view.test_get_subject.GetSubjectTestCase'))
    runner = HTMLTestRunner(report, title=report_title, description=report_des)
    runner.run(suite)
report.close()


if __name__ == '__main__':
    unittest.main()
