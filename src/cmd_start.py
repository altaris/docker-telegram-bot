# -*- coding: utf-8 -*-
"""Implentation of command `/start`.
"""

from docker_utils import (
    ContainerSelector,
    DockerCommand
)

class Start(DockerCommand):
    """Implementation of command `/start`.
    """

    def main(self):
        container_name = self.arg(
            "container_name",
            ContainerSelector(self.docker_client)
        )
        container = self.get_container(container_name)
        if container:
            self.reply(f'🔄 Starting container `{container_name}`.')
            container.start()
            self.edit_reply(f'🆗 Started container `{container_name}`.')
