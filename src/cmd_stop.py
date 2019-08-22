"""Implentation of command `/stop`.
"""

from typing import (
    List
)

from docker import DockerClient
from telegram import (
    Bot,
    Message
)

from docker_utils import (
    choose_container,
    get_container
)
from telegram_utils import (
    ask_for_confirmation,
    edit_reply,
    reply
)


NAME = "stop"
HELP = "Usage: `/stop <CONTAINER>`\nStops container `CONTAINER`."


def main(client: DockerClient,
         bot: Bot,
         message: Message,
         args: List[str]) -> None:
    """Implentation of command `/stop`.
    """
    if not args:
        choose_container(client, bot, message, NAME)
    container_name = args[0]
    if len(args) < 2:
        ask_for_confirmation(
            f'This will *stop* `{container_name}`. Are you sure?',
            bot, message, f'{NAME}:{container_name}')
    if args[1]:
        container = get_container(client, bot, message, container_name)
        if container:
            message = reply(f'🔄 Stopping container `{container_name}`.',
                            bot, message)
            container.stop()
            edit_reply(f'🆗 Stopped container `{container_name}`.', message)
