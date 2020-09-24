# -*- coding: utf-8 -*-

import logging
import re
import time
import json
import ujson
import xsmtplib
import threading

from queue import Queue
from email.mime.text import MIMEText
from email.header import Header

from .smtp import init_smtp, SendEmailPool
from .github_util import init_git

init_git()

init_smtp()
smtp_thread = SendEmailPool(0)
smtp_thread.start()