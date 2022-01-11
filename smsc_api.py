import os
import urllib.parse
from dataclasses import dataclass, asdict

import asks
import asyncclick as click
from dotenv import load_dotenv
from loguru import logger


load_dotenv()


SMSC_SENDING_URL = 'https://smsc.ru/sys/send.php'
SMSC_STATUS_URL = 'https://smsc.ru/sys/status.php'


@dataclass
class SmsMessageInfo:
    """Sms message info for sending throw smsc.ru api."""
    login: str
    psw: str
    phones: str
    mes: str
    sender: str
    fmt: int = 3
    valid: int = 1


@click.command()
@click.option(
    "--phones",
    help="Comma-separated phone numbers where SMS will be sent",
    required=True,
)
@click.option(
    "--lifetime", default=1,
    help="Lifetime in hours of undelivered messages",)
@click.option(
    "--message", default='Hello World!', help="Message for sending"
)
async def send_sms_message(**kwargs):
    phones = kwargs.get('phones')
    message = kwargs.get('message')
    sms_lifetime = kwargs.get('lifetime')
    sms_info = SmsMessageInfo(
        login=os.getenv('SMSC_LOGIN'), psw=os.getenv('SMSC_PASSWORD'),
        sender=os.getenv('SMSC_SENDER'), mes=message, phones=phones
    )
    if sms_lifetime:
        sms_info.valid = sms_lifetime
    encoded_sms_info = urllib.parse.urlencode(asdict(sms_info))
    response = await asks.get(SMSC_SENDING_URL, params=encoded_sms_info)
    logger.info('Message sent')

    sms_id = response.json().get('id')

    info_for_getting_sms_status = {
        'login': sms_info.login, 'psw': sms_info.psw,
        'phone': sms_info.phones, 'id': sms_id, 'fmt': sms_info.fmt,
    }
    encoded_status_info = urllib.parse.urlencode(info_for_getting_sms_status)
    status_response = await asks.get(
        SMSC_STATUS_URL, params=encoded_status_info)

    logger.info(f'Message status - {status_response.json()}')


if __name__ == '__main__':
    send_sms_message(_anyio_backend="trio")

