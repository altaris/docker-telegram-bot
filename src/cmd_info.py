"""Implentation of command `/info`.
"""

from typing import (
    List
)

from docker import DockerClient
from telegram import (
    Bot,
    Message
)

from docker_utils import (
    emoji_of_status,
    get_container
)
from telegram_utils import (
    reply,
    to_inline_keyboard
)


NAME = "info"
HELP = "Usage: `/info [CONTAINER]`\nProvides global informations about the " \
       "current docker daemon, or about `CONTAINER`, if specified."


def main(client: DockerClient,
         bot: Bot,
         message: Message,
         args: List[str]) -> None:
    """Implentation of command `/info`.
    """
    if not args:
        reply(
            "Select an option",
            bot,
            message,
            reply_markup=to_inline_keyboard(
                [("Docker daemon", "")] +
                [(f'{container.name} (container)', container.name)
                 for container in client.containers.list(all=True)],
                NAME
            )
        )
        return
    if args[0] == "":
        info_docker(client, bot, message)
    else:
        info_container(client, bot, message, args[0])


def info_container(client: DockerClient,
                           bot: Bot,
                           message: Message,
                           container_name: str) -> None:
    """Implentation of command `/info`.

    Retrieves and sends general informations about a container.
    """
    container = get_container(client, bot, message, container_name)
    if container is not None:
        text = f'''*Container `{container.short_id} {container.name}`:*
️️▪️ Image: `{container.image}`
️️▪️ Status: {emoji_of_status(container.status)} ({container.status})
️️▪️ Labels: {container.labels}'''
        reply(text, bot, message)


def info_docker(client: DockerClient,
                        bot: Bot,
                        message: Message) -> None:
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
    text = f'''*Docker status* 🐳⚙️
▪️ Docker version: {info["ServerVersion"]}
▪️ Memory: {int(info["MemTotal"])/1000000000} GiB
▪️ Running containers: {len(running_containers)}{running_container_list}
▪️ Restarting containers: {len(restarting_containers)}{restarting_container_list}
▪️ Paused containers: {len(paused_containers)}{paused_container_list}
▪️ Stopped containers: {len(stopped_containers)}{stopped_container_list}'''
    reply(text, bot, message)
