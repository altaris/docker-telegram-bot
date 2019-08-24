"""Implentation of command `/stop`.
"""

from docker_utils import (
    ContainerSelector,
    DockerCommand
)

class Stop(DockerCommand):
    """Implementation of command `/stop`.
    """

    def main(self):
        container_name = self.arg(
            "container_name",
            ContainerSelector(self.docker_client)
        )
        container = self.get_container(container_name)
        if container:
            self.reply(f'🔄 Stopping container `{container_name}`.')
            container.stop()
            self.edit_reply(f'🆗 Stopped container `{container_name}`.')
