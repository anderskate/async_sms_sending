import trio
import aioredis
import trio_asyncio
from quart import render_template, websocket, Response, request
from quart_trio import QuartTrio
from pydantic import BaseModel, constr, ValidationError
from loguru import logger
from hypercorn.trio import serve
from hypercorn.config import Config as HyperConfig

from smsc_api import request_smsc
from settings import Config
from db import Database


class UserSmsInput(BaseModel):
    text: constr(min_length=2, max_length=255)


app = QuartTrio(__name__, template_folder='templates')
app.config.from_mapping(Config().dict())


@app.before_serving
async def create_db_pool():
    redis_url = app.config.get('REDIS_URL')
    redis = await aioredis.from_url(redis_url, decode_responses=True)
    app.redis = redis
    app.db = Database(redis)


@app.route('/')
async def index():
    return await render_template('index.html')


@app.route('/send/', methods=['POST'])
async def posts():
    form = await request.form
    try:
        user_input = UserSmsInput(**form)
    except ValidationError as error:
        return Response(error.json(), status=400)

    phones = app.config.get('PHONES')
    sms_sending_result = await request_smsc(
        'POST', 'send',
        payload={
            'phones': phones,
            'mes': user_input.text,
            'fmt': 3, 'sender': app.config.get('SMSC_SENDER'),
        }
    )
    logger.info('SMS с сообщением - {} отправлено', user_input.text)

    await trio_asyncio.aio_as_trio(
        app.db.add_sms_mailing(
            sms_sending_result.get('id'), phones, user_input.text,
        )
    )

    return sms_sending_result


@app.websocket('/ws')
async def ws():
    while True:
        sms_mailing_ids = await trio_asyncio.aio_as_trio(
            app.db.list_sms_mailings()
        )
        sms_mailings = await trio_asyncio.aio_as_trio(
            app.db.get_sms_mailings(*sms_mailing_ids)
        )
        formatted_sms_mailings = [
            {
                "timestamp": sms.get('created_at'),
                "SMSText": sms.get('text'),
                "mailingId": str(sms.get('sms_id')),
                "totalSMSAmount": sms.get('phones_count'),
                "deliveredSMSAmount": 0,
                "failedSMSAmount": 0,
            }
            for sms in sms_mailings
        ]

        response = {
          "msgType": "SMSMailingStatus",
          "SMSMailings": formatted_sms_mailings,
        }
        await websocket.send_json(response)
        await trio.sleep(3)


@app.after_serving
async def close_db_pool():
    await trio_asyncio.asyncio_as_trio(app.redis.close())


async def run_server():
    async with trio_asyncio.open_loop() as loop:
        config = HyperConfig()
        config.bind = [f"127.0.0.1:5000"]
        config.use_reloader = True
        await serve(app, config)


if __name__ == '__main__':
    trio.run(run_server)
