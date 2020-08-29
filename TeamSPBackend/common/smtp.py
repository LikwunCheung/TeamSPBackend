# -*- coding: utf-8 -*-

from xsmtplib.xsmtplib import SMTP

from TeamSPBackend.common import *
from TeamSPBackend.common.utils import mills_timestamp
from TeamSPBackend.common.choices import InvitationStatus
from TeamSPBackend.common.config import *
from TeamSPBackend.invitation.models import Invitation

logger = logging.getLogger('django')

try:
    s = SMTP(host=GMAIL_ADDRESS, port=GMAIL_PROT, proxy_host=PROXY_HOST, proxy_port=PROXY_PORT, timeout=10)
except Exception as e:
    s = SMTP(host=GMAIL_ADDRESS, port=GMAIL_PROT, timeout=10)

connected = False


def init_smtp():
    global connected

    logger.info(u'[SMTP] Initialize SMTP Service: ' + GMAIL_ADDRESS + ':' + str(GMAIL_PROT))
    try:
        s.ehlo()
        s.starttls()
        s.login(GMAIL_ACCOUNT, GMAIL_PASSWORD)
        connected = True
        logger.info(u'[SMTP] Initialize SMTP Service Success!')
    except Exception as e:
        print(e)


def send_email(coordinator, address, content):
    global connected

    if not connected:
        return False

    try:
        logger.info(u'[SMTP] Sending Email: %s %s %s' % (coordinator, address, content))

        message = MIMEText(content, PLAIN, UTF8)
        message[FROM] = Header(coordinator, UTF8)
        message[TO] = Header(address, UTF8)
        message[SUBJECT] = Header(INVITATION_TITLE, UTF8)

        s.sendmail(GMAIL_ACCOUNT, address, message.as_string())
        return True
    except Exception as e:
        print(e)
        return False


class SendEmailPool(threading.Thread):

    def __init__(self, size=0):
        self.count = 0
        self.size = size
        self.pool = Queue(self.size)
        threading.Thread.__init__(self)

    def put_task(self, id, coordinator, address, content):
        logger.info(u'[SMTP] Receive: %d %s %s' % (id, address, content))

        self.pool.put(dict(
            id=id,
            coordinator=coordinator,
            email=address,
            text=content,
        ))

    def consume(self):
        task = self.pool.get(block=True, timeout=None)

        logger.info(u'[SMTP] Send Email: %d %s' % (self.count, str(task)))
        invite = Invitation.objects.get(invitation_id=task['id'], status=InvitationStatus.waiting.value.key)

        if invite is None or invite.expired <= mills_timestamp():
            return

        if send_email(task['coordinator'], task['email'], task['text']):
            invite.status = InvitationStatus.sent.value.key
            invite.save()

    def run(self):
        self.count += 1
        self.consume()
