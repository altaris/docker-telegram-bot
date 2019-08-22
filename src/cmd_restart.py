"""Implentation of command `/restart`.
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


NAME = "restart"
HELP = "Usage: `/restart <CONTAINER>`\nRestarts container `CONTAINER`."


def main(client: DockerClient,
         bot: Bot,
         message: Message,
         args: List[str]) -> None:
    """Implentation of command `/restart`.
    """
    if not args:
        choose_container(client, bot, message, NAME)
        return
    container_name = args[0]
    container = get_container(client, bot, message, container_name)
    if container:
        message = reply(f'🔄 Restarting container `{container_name}`.',
                        bot, message)
        container.restart()
        edit_reply(f'🆗 Restarted container `{container_name}`.', message)
