"""Implementation of the commands supported by of the bot.

A command is a callable that has type ``commands.Command``, and decorated by
``command.__command__``.
"""

import logging
from typing import (
    Callable,
    Dict,
    List,
    Optional,
    Union
)

import docker
from docker import (
    DockerClient
)
from telegram import (
    Bot,
    KeyboardButton,
    Update
)

from docker_utils import (
    get_container
)
from telegram_utils import (
    edit_reply,
    expect_arg_count,
    expect_max_arg_count,
    reply,
    reply_error
)

Command = Callable[[DockerClient, Bot, Update, List[str]], None]


COMMANDS = {}  # type: Dict[str, Command]
COMMANDS_HELP = {}  # type: Dict[str, str]
COMMAND_KEYBOARD = [
    ["/info", "/help"],
    ["/start", "/stop", "/restart"]
]  # type: List[List[Union[str, KeyboardButton]]]


def __command__(name: Optional[str] = None, help_msg: str = ""):
    """Decorator for command callbacks.

    A command has type commands.Command. This decorator wraps it to catch and
    report ``docker.errors.APIError exceptions``.
    """
    def decorator(cmd: Command) -> Command:
        def wrapper(client: DockerClient,
                    bot: Bot,
                    update: Update,
                    args: List[str]) -> None:
            try:
                logging.debug("Called command %s with args %s", name, args)
                cmd(client, bot, update, args)
            except docker.errors.APIError as error:
                reply_error(f'Docker daemon raised an API error: {str(error)}',
                            bot, update)
        if name:
            # pylint: disable=global-statement
            global COMMANDS
            global COMMANDS_HELP
            COMMANDS[name] = wrapper
            COMMANDS_HELP[name] = help_msg
        return wrapper
    return decorator


@__command__(
    "help",
    "Usage `/help <COMMAND>`\nDisplays help message about `COMMAND` if "
    "available.")
def command_help(client: DockerClient,
                 bot: Bot,
                 update: Update,
                 args: List[str]) -> None:
    """Implentation of command `/help`.
    """
    # pylint: disable=unused-argument
    if not expect_arg_count(1, args, bot, update):
        return
    command_name = args[0]
    if command_name not in COMMANDS:
        reply_error(f'Command `{command_name}` not found.', bot, update)
        return
    command_doc = COMMANDS_HELP.get(command_name, None)
    if command_doc is None:
        reply(f'No help available for command `{command_name}`.',
              bot, update)
    else:
        reply(f'''🆘 *Help for command `{command_name}`* 🆘
{command_doc}''',
              bot, update)


@__command__(
    "info",
    "Usage: `/info [CONTAINER]\nProvides global informations about the "
    "current docker daemon, or about `CONTAINER`, if specified.")
def command_info(client: DockerClient,
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


@__command__(
    "restart",
    "Usage: `/restart <CONTAINER>`\nRestarts container `CONTAINER`.")
def command_restart(client: DockerClient,
                    bot: Bot,
                    update: Update,
                    args: List[str]) -> None:
    """Implentation of command `/restart`.
    """
    if not expect_arg_count(1, args, bot, update):
        return
    container_name = args[0]
    container = get_container(client, bot, update, container_name)
    if container:
        message = reply(f'🔄 Restarting container `{container_name}`.',
                        bot, update)
        container.restart()
        edit_reply(f'🆗 Restarted container `{container_name}`.', message)


@__command__(
    "start",
    "Usage: `/start <CONTAINER>`\nStarts container `CONTAINER`.")
def command_start(client: DockerClient,
                  bot: Bot,
                  update: Update,
                  args: List[str]) -> None:
    """Implentation of command `/start`.
    """
    if not expect_arg_count(1, args, bot, update):
        return
    container_name = args[0]
    container = get_container(client, bot, update, container_name)
    if container:
        message = reply(f'🔄 Starting container `{container_name}`.',
                        bot, update)
        container.start()
        edit_reply(f'🆗 Started container `{container_name}`.', message)


@__command__(
    "stop",
    "Usage: `/stop <CONTAINER>`\nStops container `CONTAINER`.")
def command_stop(client: DockerClient,
                 bot: Bot,
                 update: Update,
                 args: List[str]) -> None:
    """Implentation of command `/stop`.
    """
    if not expect_arg_count(1, args, bot, update):
        return
    container_name = args[0]
    container = get_container(client, bot, update, container_name)
    if container:
        message = reply(f'🔄 Stopping container `{container_name}`.',
                        bot, update)
        container.stop()
        edit_reply(f'🆗 Stopped container `{container_name}`.', message)
