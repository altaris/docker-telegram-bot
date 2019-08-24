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

    def main(self):
        container_name = self.arg(
            "container_name",
            ContainerSelector(self.docker_client)
        )
        container = self.get_container(container_name)
        if container:
            self.reply(f'🔄 Pausing container `{container_name}`.')
            container.pause()
            self.edit_reply(f'🆗 Paused container `{container_name}`.')
