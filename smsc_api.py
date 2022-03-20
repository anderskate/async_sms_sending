import asyncio
import os
import urllib.parse
from dataclasses import dataclass, asdict
from contextvars import ContextVar
from typing import Optional
from unittest.mock import patch

import asks
import asyncclick as click
from dotenv import load_dotenv
from loguru import logger


load_dotenv()


SMSC_SENDING_URL = 'https://smsc.ru/sys/send.php'
SMSC_STATUS_URL = 'https://smsc.ru/sys/status.php'

smsc_login: ContextVar[str] = ContextVar('smsc_login')
smsc_password: ContextVar[str] = ContextVar('smsc_password')
smsc_login.set(os.getenv('SMSC_LOGIN'))
smsc_password.set(os.getenv('SMSC_PASSWORD'))


class SmscApiError(Exception):
    def __init__(self, msg_error):
        self.msg_error = msg_error


@dataclass
class SmsMessageInfo:
    """Data for sending msg throw smsc.ru api."""
    login: str
    psw: str
    phones: str
    mes: str
    sender: str
    fmt: int = 3
    valid: int = 1


@dataclass
class SmsStatusInfo:
    """Data for getting info about sending sms throw smsc.ru api."""
    login: str
    psw: str
    phone: str
    id: int
    fmt: int = 3


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


async def request_smsc(
        http_method: str, api_method: str,
        login: Optional[str] = None,
        password: Optional[str] = None, payload: dict = {},
) -> dict:
    """Send request to SMSC.ru service.

    Args:
        http_method (str): E.g. 'GET' or 'POST'.
        api_method (str): E.g. 'send' or 'status'.
        login (str): Login for account on smsc.ru.
        password (str): Password for account on smsc.ru.
        payload (dict): Additional request params, override default ones.

    Returns:
        dict: Response from smsc.ru API.

    Raises:
        SmscApiError:
        If smsc.ru API response status is not 200 or JSON response
        has "error_code" inside.
    """
    login = login or smsc_login.get()
    password = password or smsc_password.get()

    api_methods_map = {
        'send': (SMSC_SENDING_URL, SmsMessageInfo),
        'status': (SMSC_STATUS_URL, SmsStatusInfo),
    }
    http_methods_map = {'GET': asks.get, 'POST': asks.post}

    api_method_url, dataclass_handler = api_methods_map.get(
        api_method, (None, None)
    )
    if not api_method_url:
        raise SmscApiError(f'API method {api_method} is not supported')
    http_asks = http_methods_map.get(http_method)
    if not http_asks:
        raise SmscApiError(f'HTTP method {http_method} is not supported')

    try:
        sms_info = dataclass_handler(login=login, psw=password, **payload)
    except TypeError as error:
        raise SmscApiError(f'Incorrect params for request. Error - {error}')
    encoded_sms_info = urllib.parse.urlencode(asdict(sms_info))
    logger.info('Send request to smsc.ru')
    response = await http_asks(api_method_url, params=encoded_sms_info)

    return response.json()


async def main():
    """"""
    with patch(
            '__main__.request_smsc', {'id': 52, 'cnt': 1}
    ) as mock_sending_sms:
        print(mock_sending_sms)

    with patch(
            '__main__.request_smsc',
            {
                'status': 1, 'last_date': '20.03.2022 07:56:03',
                'last_timestamp': 1647752163, 'err': 200,
            }
    ) as mock_getting_status:
        print(mock_getting_status)


if __name__ == '__main__':
    asyncio.run(main())
