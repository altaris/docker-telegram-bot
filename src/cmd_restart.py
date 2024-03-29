# -*- coding: utf-8 -*-
"""Implentation of command `/restart`.
"""

from docker_utils import (
    ContainerSelector,
    DockerCommand
)

class Restart(DockerCommand):
    """Implementation of command `/restart`.
    """

    __HELP__ = """▪️ Usage: `/restart CONTAINER`:
Restarts a container."""

    def main(self):
        container_name = self.arg(
            "0",
            ContainerSelector(self.docker_client),
            "Choose a container to *restart*:"
        )
        container = self.get_container(container_name)
        if container:
            self.reply(f'🔄 Restarting container `{container_name}`.')
            container.restart()
            self.edit_reply(f'🆗 Restarted container `{container_name}`.')
