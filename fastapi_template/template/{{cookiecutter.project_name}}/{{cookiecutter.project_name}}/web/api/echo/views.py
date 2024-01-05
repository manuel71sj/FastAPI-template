from fastapi import APIRouter
from loguru import logger

from {{cookiecutter.project_name}}.settings import settings
from {{cookiecutter.project_name}}.web.api.echo.schema import Message

router = APIRouter()


@router.post("/", response_model=Message)
async def send_echo_message(
    incoming_message: Message,
) -> Message:
    """
    Sends echo back to user.

    :param incoming_message: incoming message.
    :returns: message same as the incoming.
    """
    logger.info(settings.users_secret)
    logger.bind(
        payload={
            'limit': 1,
            'offset': 10,
        },
    ).info('get_dummy_models 天')

    a = 1 / 0  # noqa: F841
    return incoming_message
