"""Implentation of command `/start`.
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
    edit_reply,
    reply
)


NAME = "start"
HELP = "Usage: `/start <CONTAINER>`\nStarts container `CONTAINER`."


def main(client: DockerClient,
         bot: Bot,
         message: Message,
         args: List[str]) -> None:
    """Implentation of command `/start`.
    """
    if not args:
        choose_container(client, bot, message, NAME)
        return
    container_name = args[0]
    container = get_container(client, bot, message, container_name)
    if container:
        message = reply(f'🔄 Starting container `{container_name}`.',
                        bot, message)
        container.start()
        edit_reply(f'🆗 Started container `{container_name}`.', message)
