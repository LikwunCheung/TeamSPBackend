import hashlib
import names
from TeamSPBackend.common.config import SALT
from TeamSPBackend.common.utils import mills_timestamp
from TeamSPBackend.common.choices import Status, Roles
from TeamSPBackend.team.models import Team
from TeamSPBackend.account.models import Account, User


def createAdmin():
    # create account
    timestamp = mills_timestamp()
    username = "admin"
    password = "admin"
    email = "admin@gmail.com"
    status = Status.valid.value.key
    create_date = timestamp
    update_date = timestamp
    first_name = "admin"
    last_name = "test"
    role = Roles.admin.value.key
    md5 = encrypt(password)
    account = Account(username=username, email=email, password=md5,
                      status=status, create_date=create_date, update_date=update_date)
    account.save()

    # create user
    user = User(account_id=account.account_id, username=username, first_name=first_name, last_name=last_name,
                role=role, status=status, create_date=create_date, update_date=update_date, email=email)
    user.save()


def createSupervisor(first_name, last_name):
    timestamp = mills_timestamp()
    username = first_name
    password = "supervisor"
    email = username + "@gmail.com"
    status = Status.valid.value.key
    create_date = timestamp
    update_date = timestamp
    first_name = first_name
    last_name = last_name
    role = Roles.supervisor.value.key
    md5 = encrypt(password)
    account = Account(username=username, email=email, password=md5,
                      status=status, create_date=create_date, update_date=update_date)
    account.save()

    # create user
    user = User(account_id=account.account_id, username=username, first_name=first_name, last_name=last_name,
                role=role, status=status, create_date=create_date, update_date=update_date, email=email)
    user.save()


def encrypt(password):
    password = password + SALT
    md5 = hashlib.sha3_256(password.encode()).hexdigest()
    return md5
