import os

import pytest
from dotenv import load_dotenv

from smsc_api import request_smsc, SmscApiError


load_dotenv()


@pytest.mark.asyncio
async def test_sending_sms():
    """Test that sms sent is successful."""
    response = await request_smsc(
        'POST', 'send',
        payload={
            'phones': '79771725757',
            'mes': 'Hello World!',
            'fmt': 3, 'sender': os.getenv('SMSC_SENDER'),
        }
    )

    correct_response = {'id': 'Test ID', 'cnt': 1}

    assert response.keys() == correct_response.keys()


async def test_incorrect_api_method():
    """Check that sending request with incorrect api method raise Exception"""
    with pytest.raises(SmscApiError):
        await request_smsc(
            'POST', 'incorrect_api_method',
            payload={
                'phones': '79771725756',
                'mes': 'Hello World2!',
                'fmt': 3, 'sender': os.getenv('SMSC_SENDER'),
            }
        )


async def test_incorrect_request_params():
    """Test that request raises exception with incorrect params.

    For example, there is no param - Phone number.
    """
    with pytest.raises(SmscApiError):
        await request_smsc(
            'POST', 'send',
            payload={
                'mes': 'Hello World3!',
                'fmt': 3, 'sender': os.getenv('SMSC_SENDER'),
            }
        )
