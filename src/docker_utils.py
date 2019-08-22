"""Various docker utilities.
"""

from typing import (
    Optional
)

import docker
from docker.models.containers import (
    Container
)
from telegram import (
    Bot,
    Message
)

from telegram_utils import (
    NotEnoughArguments,
    reply,
    reply_error,
    to_inline_keyboard
)


def choose_container(client: docker.DockerClient,
                     bot: Bot,
                     message: Message,
                     callback_prefix: str) -> None:
    """Gets the user to choose a container.
    """

    reply(
        "Select a container",
        bot,
        message,
        reply_markup=to_inline_keyboard([
            (
                f'{container.name} {emoji_of_status(container.status)}',
                container.name
            ) for container in client.containers.list(all=True)],
            callback_prefix
        )
    )
    raise NotEnoughArguments


def emoji_of_status(status: str) -> str:
    """Returns the emoji associated to a docker container status.

    The emojis are as follows:
    * `exited`: ⏹,
    * `paused`: ⏸,
    * `restarting`: ↩,
    * `running`: ▶,
    * otherwise: ❓.
    """
    return {
        "exited": "⏹"
        "paused": "⏸",
        "restarting": "↩",
        "running": "▶",
    }.get(status, "❓")


def get_container(client: docker.DockerClient,
                  bot: Bot,
                  message: Message,
                  container_name: str) -> Optional[Container]:
    """Gets a container.

    If the container does not exist, return ``None`` and reports.
    """
    container = None  # type: Optional[Container]
    try:
        container = client.containers.get(container_name)
    except docker.errors.NotFound:
        reply_error(f'Container \"{container_name}\" not found.', bot, message)
    return container
