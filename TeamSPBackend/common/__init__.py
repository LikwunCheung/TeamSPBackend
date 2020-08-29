# -*- coding: utf-8 -*-

import logging
import re
import time
import ujson
import smtplib
import threading

from queue import Queue
from email.mime.text import MIMEText
from email.header import Header

from .smtp import init_smtp, SendEmailPool


init_smtp()
smtp_thread = SendEmailPool(0)
smtp_thread.start()