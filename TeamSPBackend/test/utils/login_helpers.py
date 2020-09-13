import hashlib
import names
from TeamSPBackend.common.config import SALT
from TeamSPBackend.common.utils import mills_timestamp
from TeamSPBackend.common.choices import Status, Roles
from TeamSPBackend.team.models import Team
from TeamSPBackend.account.models import Account, User


def encrypt(password):
    password = password + SALT
    md5 = hashlib.sha3_256(password.encode()).hexdigest()
    return md5


def login(client):
    # login first
    username = "admin"
    password = "admin"
    credentials = {
        'username': username,
        'password': password
    }
    response = client.post('/api/v1/account/login',
                           data=credentials, content_type="application/json")
    user = User.objects.get(username=username)
    session_data = dict(
        id=user.user_id,
        name=user.get_name(),
        role=user.role,
        is_login=True,
    )
    session = client.session
    session['user'] = session_data
