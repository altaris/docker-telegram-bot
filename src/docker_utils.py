# -*- coding: utf-8 -*-
"""Various docker utilities.
"""

from typing import (
    Optional,
    Sequence,
    Tuple,
    Union
)

from docker import (
    DockerClient
)
import docker.errors
from docker.models.containers import (
    Container
)

from telecom.command import (
    Command
)
from telecom.selector import (
    ArgumentSelector
)


class ContainerSelector(ArgumentSelector):
    """Selects a container.
    """

    def __init__(self, docker_client: DockerClient):
        self._docker_client = docker_client

    def option_list(self) -> Sequence[Union[str, Tuple[str, str]]]:
        return [
            (
                f'{container.name} {emoji_of_status(container.status)}',
                container.name
            )
            for container in self._docker_client.containers.list(all=True)
        ]


# pylint: disable=abstract-method
class DockerCommand(Command):
    """An abstract command that interacts with the docker daemon.

    A ``docker.DockerClient`` MUST be given as a default argument for key
    ``docker_client``.
    """

    def get_container(self,
                      container_name: str) -> Optional[Container]:
        """Gets a container.

        If the container does not exist, return ``None`` and reports.
        """
        container = None  # type: Optional[Container]
        try:
            container = self.docker_client.containers.get(container_name)
        except docker.errors.NotFound:
            self.reply_error(f'Container \"{container_name}\" not found.')
        return container

    @property
    def docker_client(self) -> DockerClient:
        """Returns the ``docker.DockerClient`` of this command.
        """
        client = self._args_dict.get("docker_client", None)
        if not isinstance(client, DockerClient):
            raise ValueError(
                'A DockerCommand must have a DockerClient as default value '
                'for key "docker_client"'
            )
        return client


def emoji_of_status(status: str) -> str:
    """Returns the emoji associated to a docker container status.

    The emojis are as follows:
        * ``exited``: ⏹,
        * ``paused``: ⏸,
        * ``restarting``: ↩,
        * ``running``: ▶,
        * otherwise: ❓.
    """
    return {
        "exited": "⏹",
        "paused": "⏸",
        "restarting": "↩",
        "running": "▶"
    }.get(status, "❓")
