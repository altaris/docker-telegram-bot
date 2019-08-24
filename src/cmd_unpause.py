# -*- coding: utf-8 -*-
"""Implentation of command `/unpause`.
"""

from docker_utils import (
    ContainerSelector,
    DockerCommand
)

class Unpause(DockerCommand):
    """Implementation of command `/unpause`.
    """

    __HELP__ = """▪️ Usage: `/unpause CONTAINER`:
Unpauses a container."""

    def main(self):
        container_name = self.arg(
            "container_name",
            ContainerSelector(self.docker_client)
        )
        container = self.get_container(container_name)
        if container:
            self.reply(f'🔄 Unpausing container `{container_name}`.')
            container.unpause()
            self.edit_reply(f'🆗 Unpaused container `{container_name}`.')
