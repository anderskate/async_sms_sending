import os
import urllib.parse
from dataclasses import dataclass, asdict

import asks
import asyncclick as click
from dotenv import load_dotenv


load_dotenv()


SMSC_API_URL = 'https://smsc.ru/sys/send.php'


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
        sender=os.getenv('SMSC_SENDER'), mes=message, phones=phones,
    )
    if sms_lifetime:
        sms_info.valid = sms_lifetime
    encoded_sms_info = urllib.parse.urlencode(asdict(sms_info))
    response = await asks.get(SMSC_API_URL, params=encoded_sms_info)
    print(response.json())


if __name__ == '__main__':
    send_sms_message(_anyio_backend="trio")

