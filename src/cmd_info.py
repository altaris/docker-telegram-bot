# -*- coding: utf-8 -*-
"""Implentation of command `/info`.
"""

from typing import (
    List,
    Sequence,
    Tuple,
    Union
)

from docker_utils import (
    ContainerSelector,
    DockerCommand,
    emoji_of_status
)


class InfoSelector(ContainerSelector):
    """Adds the `Docker daemon` option to `docker_utils.ContainerSelector`.
    """

    def option_list(self) -> Sequence[Union[str, Tuple[str, str]]]:
        item = [
            ("Docker daemon 🐳", "")
        ]  # type: List[Union[str, Tuple[str, str]]]
        return item + list(ContainerSelector.option_list(self))


class Info(DockerCommand):
    """Implentation of command `/info`.
    """

    __HELP__ = """▪️ Usage: `/info`:
Displays informations about the docker "daemon.
▪️ Usage: `/info CONTAINER`:
Displays informations about a container."""

    def info_container(self, container_name: str) -> None:
        """Implentation of command `/info`.

        Retrieves and sends general informations about a container.
        """
        container = self.get_container(container_name)
        if container is not None:
            labels_formatted = "\n".join([
                f'  🏷 `{key}`: `{val}`'
                for key, val in container.labels
            ])
            text = f'''*Container *`{container.short_id} {container.name}`*:*
▪️ Image: `{container.image}`
▪️ Status: {emoji_of_status(container.status)} ({container.status})
▪️ Labels: {labels_formatted}'''
            self.reply(text)


    def info_docker(self) -> None:
        """Implentation of command `/info`.

        Retrieves and sends general informations about the docker daemon.
        """
        info = self.docker_client.info()
        running_containers = self.docker_client.containers.list(
            filters={"status": "running"}
        )
        running_container_list = "\n".join([''] + [
            f'     - `{c.name}`' for c in running_containers
        ])
        restarting_containers = self.docker_client.containers.list(
            filters={"status": "restarting"}
        )
        restarting_container_list = "\n".join([''] + [
            f'     - `{c.name}`' for c in restarting_containers
        ])
        paused_containers = self.docker_client.containers.list(
            filters={"status": "paused"}
        )
        paused_container_list = "\n".join([''] + [
            f'     - `{c.name}`' for c in paused_containers
        ])
        stopped_containers = self.docker_client.containers.list(
            filters={"status": "exited"}
        )
        stopped_container_list = "\n".join([''] + [
            f'     - `{c.name}`' for c in stopped_containers
        ])
        text = f'''*Docker status* 🐳⚙️
▪️ Docker version: {info["ServerVersion"]}
▪️ Memory: {int(info["MemTotal"])/1000000000} GiB
▪️ Running containers: {len(running_containers)}{running_container_list}
▪️ Restarting containers: {len(restarting_containers)}{restarting_container_list}
▪️ Paused containers: {len(paused_containers)}{paused_container_list}
▪️ Stopped containers: {len(stopped_containers)}{stopped_container_list}'''
        self.reply(text)

    def main(self) -> None:
        item = self.arg("0", InfoSelector(self.docker_client))
        if item == "":
            self.info_docker()
        else:
            self.info_container(item)
