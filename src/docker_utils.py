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
    Update
)

from telegram_utils import (
    reply_error
)


def get_container(client: docker.DockerClient,
                  bot: Bot,
                  update: Update,
                  container_name: str) -> Optional[Container]:
    """Gets a container.

    If the container does not exist, return ``None`` and reports.
    """
    container = None  # type: Optional[Container]
    try:
        container = client.containers.get(container_name)
    except docker.errors.NotFound:
        reply_error(f'Container \"{container_name}\" not found.', bot, update)
    return container
