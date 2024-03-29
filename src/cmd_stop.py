# -*- coding: utf-8 -*-
"""Implentation of command `/stop`.
"""

from docker_utils import (
    ContainerSelector,
    DockerCommand
)

class Stop(DockerCommand):
    """Implementation of command `/stop`.
    """

    __HELP__ = """▪️ Usage: `/stop CONTAINER`:
Stops a container."""

    def main(self):
        container_name = self.arg(
            "0",
            ContainerSelector(self.docker_client),
            "Choose a container to *stop*:"
        )
        container = self.get_container(container_name)
        if container:
            self.reply(f'🔄 Stopping container `{container_name}`.')
            container.stop()
            self.edit_reply(f'🆗 Stopped container `{container_name}`.')
