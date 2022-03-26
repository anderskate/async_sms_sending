from quart import render_template, websocket, Response, request
from quart_trio import QuartTrio
from pydantic import BaseModel, constr, ValidationError
from loguru import logger

from smsc_api import request_smsc
from settings import Config


class UserSmsInput(BaseModel):
    text: constr(min_length=2, max_length=255)


app = QuartTrio(__name__, template_folder='templates')
app.config.from_mapping(Config().dict())


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

    sms_sending_result = await request_smsc(
        'POST', 'send',
        payload={
            'phones': app.config.get('PHONES'),
            'mes': user_input.text,
            'fmt': 3, 'sender': app.config.get('SMSC_SENDER'),
        }
    )
    logger.info('SMS с сообщением - {} отправлено', user_input.text)
    return sms_sending_result


@app.websocket('/ws')
async def ws():
    while True:
        data = await websocket.receive()
        await websocket.send(f"echo {data}")


if __name__ == '__main__':
    app.run(port=5000)
