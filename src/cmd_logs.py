# -*- coding: utf-8 -*-
"""Implentation of command `/logs`.
"""

from docker_utils import (
    ContainerSelector,
    DockerCommand
)

class Logs(DockerCommand):
    """Implementation of command `/start`.
    """

    __HELP__ = """▪️ Usage: `/logs CONTAINER`:
Shows logs of a container."""

    LOG_LINES_TO_FETCH: int = 25

    def main(self):
        container_name = self.arg(
            "0",
            ContainerSelector(self.docker_client),
            "Choose a container:"
        )
        container = self.get_container(container_name)
        if container:
            logs_raw = container.logs(tail=Logs.LOG_LINES_TO_FETCH)
            logs_lines = logs_raw.decode("UTF-8").split("\n")
            logs_formatted = "\n".join(
                [f'▪️ `{line}`' for line in logs_lines if line]
            )
            self.reply(
                f'🗒 Logs for container `{container_name}` ' +
                f'(last *{Logs.LOG_LINES_TO_FETCH}* lines):\n{logs_formatted}'
            )
