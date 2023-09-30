import datetime
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any

from aiogram.utils.markdown import quote_html
from bson import ObjectId

from myresearch.consts import RolesType
from myresearch.core import settings

log = logging.getLogger(__name__)

def send_mail(to_email: str, subject: str, text: str):
    if settings.emulate_mail_sending is True:
        log.info(f'emulating mail sending to {to_email}\n{text}')
        return

    msg = MIMEMultipart()
    msg['From'] = settings.mailru_login
    msg['To'] = to_email
    msg['Subject'] = subject

    body = quote_html(text)
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP_SSL(settings.mailru_server, settings.mailru_port)
        server.login(settings.mailru_login, settings.mailru_password)
        server.sendmail(settings.mailru_login, to_email, msg.as_string())
        server.quit()
    except Exception as e:
        log.exception(e)


def roles_to_list(roles: RolesType) -> list[str]:
    if isinstance(roles, str):
        roles = [roles]
    elif isinstance(roles, set):
        roles = list(roles)
    elif isinstance(roles, list):
        pass
    else:
        raise TypeError("bad type for roles")
    return roles

def normalize_response(data: Any) -> Any:
    if isinstance(data, list):
        new_data: list[Any] = [None for _ in range(len(data))]
        for i, v in enumerate(data):
            if isinstance(v, ObjectId):
                new_data[i] = str(v)
            else:
                new_data[i] = normalize_response(v)

    elif isinstance(data, dict):
        new_data: dict = {}
        for k, v in data.items():
            if isinstance(v, ObjectId):
                new_data[k] = str(v)
            else:
                new_data[k] = normalize_response(v)

    elif isinstance(data, ObjectId):
        new_data: str = str(data)

    else:
        new_data = data

    return new_data