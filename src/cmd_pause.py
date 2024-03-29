# -*- coding: utf-8 -*-
"""Implentation of command `/pause`.
"""

from docker_utils import (
    ContainerSelector,
    DockerCommand
)

class Pause(DockerCommand):
    """Implementation of command `/pause`.
    """

    __HELP__ = """▪️ Usage: `/pause CONTAINER`:
Pauses a container."""

    def main(self):
        container_name = self.arg(
            "0",
            ContainerSelector(self.docker_client),
            "Choose a container to *pause*:"
        )
        container = self.get_container(container_name)
        if container:
            self.reply(f'🔄 Pausing container `{container_name}`.')
            container.pause()
            self.edit_reply(f'🆗 Paused container `{container_name}`.')
