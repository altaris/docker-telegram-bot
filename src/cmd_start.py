"""Implentation of command `/start`.
"""

from typing import (
    List
)

from docker import DockerClient
from telegram import (
    Bot,
    Update
)

from docker_utils import (
    get_container
)
from telegram_utils import (
    edit_reply,
    expect_arg_count,
    reply
)


NAME = "start"
HELP = "Usage: `/start <CONTAINER>`\nStarts container `CONTAINER`."


def main(client: DockerClient,
         bot: Bot,
         update: Update,
         args: List[str]) -> None:
    """Implentation of command `/start`.
    """
    if not expect_arg_count(1, args, bot, update):
        return
    container_name = args[0]
    container = get_container(client, bot, update, container_name)
    if container:
        message = reply(f'🔄 Starting container `{container_name}`.',
                        bot, update)
        container.start()
        edit_reply(f'🆗 Started container `{container_name}`.', message)
