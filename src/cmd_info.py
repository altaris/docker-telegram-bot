"""Implentation of command `/info`.
"""

from typing import (
    List
)

from docker import DockerClient
from telegram import (
    Bot,
    Update
)

from docker_utils import (
    get_container
)
from telegram_utils import (
    expect_max_arg_count,
    reply
)


NAME = "info"
HELP = "Usage: `/info [CONTAINER]`\nProvides global informations about the " \
       "current docker daemon, or about `CONTAINER`, if specified."


def main(client: DockerClient,
         bot: Bot,
         update: Update,
         args: List[str]) -> None:
    """Implentation of command `/info`.
    """
    if not expect_max_arg_count(1, args, bot, update):
        return
    if not args:
        command_info_docker(client, bot, update)
    else:
        command_info_container(client, bot, update, args[0])


def command_info_container(client: DockerClient,
                           bot: Bot,
                           update: Update,
                           container_name: str) -> None:
    """Implentation of command `/info`.

    Retrieves and sends general informations about a container.
    """
    container = get_container(client, bot, update, container_name)
    if container is not None:
        message = f'''*Container `{container.short_id} {container.name}`:*
️️▪️ Image: {container.image}
️️▪️ Status: {container.status}
️️▪️ Labels: {container.labels}'''
    reply(message, bot, update)


def command_info_docker(client: DockerClient,
                        bot: Bot,
                        update: Update,) -> None:
    """Implentation of command `/info`.

    Retrieves and sends general informations about the docker daemon.
    """
    info = client.info()
    running_containers = client.containers.list(filters={"status": "running"})
    running_container_list = "\n".join([''] + [
        f'     - `{c.name}`' for c in running_containers])
    restarting_containers = client.containers.list(
        filters={"status": "restarting"})
    restarting_container_list = "\n".join([''] + [
        f'     - `{c.name}`' for c in restarting_containers])
    paused_containers = client.containers.list(filters={"status": "paused"})
    paused_container_list = "\n".join([''] + [
        f'     - `{c.name}`' for c in paused_containers])
    stopped_containers = client.containers.list(filters={"status": "exited"})
    stopped_container_list = "\n".join([''] + [
        f'     - `{c.name}`' for c in stopped_containers])
    message = f'''*Docker status* 🐳⚙️
▪️ Docker version: {info["ServerVersion"]}
▪️ Memory: {info["MemTotal"]}
▪️ Running containers: {len(running_containers)}{running_container_list}
▪️ Restarting containers: {len(restarting_containers)}{restarting_container_list}
▪️ Paused containers: {len(paused_containers)}{paused_container_list}
▪️ Stopped containers: {len(stopped_containers)}{stopped_container_list}'''
    reply(message, bot, update)
