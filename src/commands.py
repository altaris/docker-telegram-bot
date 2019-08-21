import docker
from docker import DockerClient
import logging
from telegram import (
    Bot, KeyboardButton, ParseMode, ReplyKeyboardMarkup, Update)
from typing import Callable, Dict, List, Optional, Union


from utils import *


Command = Callable[[DockerClient, Bot, Update, List[str]], None]


commands = {}  # type: Dict[str, Command]
commands_help = {}  # type: Dict[str, str]
command_keyboard = [
    ["/start", "/info", "/help"],
    ["/restart"]
]  # type: List[List[Union[str, KeyboardButton]]]


def __command__(name: Optional[str] = None, help_msg: str = ""):
    """Decorator for command callbacks.

    A command has type commands.Command. This decorator wraps it to catch and
    report docker.errors.APIError exceptions.
    """
    def decorator(cmd: Command) -> Command:
        def wrapper(client: DockerClient,
                    bot: Bot,
                    update: Update,
                    args: List[str]) -> None:
            try:
                logging.debug(f'Called command {name} with args {args}')
                cmd(client, bot, update, args)
            except docker.errors.APIError as e:
                reply_error(f'Docker daemon raised an API error: {str(e)}',
                            bot, update)
        if name:
            global commands
            global commands_help
            commands[name] = wrapper
            commands_help[name] = help_msg
        return wrapper
    return decorator


@__command__(
    "help",
    """Usage `/help <COMMAND>`
Displays help message about `COMMAND` if available.""")
def command_help(client: DockerClient,
                 bot: Bot,
                 update: Update,
                 args: List[str]) -> None:
    if not expect_arg_count(1, args, bot, update):
        return
    command_name = args[0]
    if command_name not in commands:
        reply_error(f'Command `{command_name}` not found.', bot, update)
        return
    command_doc = commands_help.get(command_name, None)
    if command_doc is None:
        reply(f'No help available for command `{command_name}`.',
              bot, update)
    else:
        reply(f'''🆘 *Help for command `{command_name}`* 🆘
{command_doc}''',
              bot, update)


@__command__(
    "info",
    """Usage: `/info [CONTAINER]`
Provides global informations about the current docker daemon, or about `CONTAINER`, if specified.""")
def command_info(client: DockerClient,
                 bot: Bot,
                 update: Update,
                 args: List[str]) -> None:
    if not expect_max_arg_count(1, args, bot, update):
        return
    if len(args) == 0:
        command_info_docker(client, bot, update)
    else:
        command_info_container(client, bot, update, args[0])


def command_info_container(client: DockerClient,
                           bot: Bot,
                           update: Update,
                           container_name: str) -> None:
    c = get_container(client, bot, update, container_name)
    if c is not None:
        message = f'''*Container `{c.short_id} {c.name}`:*
️️▪️ Image: {c.image}
️️▪️ Status: {c.status}
️️▪️ Labels: {c.labels}'''
    reply(message, bot, update)


def command_info_docker(client: DockerClient,
                        bot: Bot,
                        update: Update,) -> None:
    info = client.info()
    running_container_list = "\n".join([''] + [
        f'     - `{c.name}`' for c in
        client.containers.list(filters={"status": "running"})
    ])
    paused_container_list = "\n".join([''] + [
        f'     - `{c.name}`' for c in
        client.containers.list(filters={"status": "paused"})
    ])
    stopped_container_list = "\n".join([''] + [
        f'     - `{c.name}`' for c in
        client.containers.list(filters={"status": "exited"})
    ])
    message = f'''*Docker status* 🐳⚙️
▪️ Docker version: {info["ServerVersion"]}
▪️ Memory: {info["MemTotal"]}
▪️ Running containers: {info["ContainersRunning"]}{running_container_list}
▪️ Paused containers: {info["ContainersPaused"]}{paused_container_list}
▪️ Stopped containers: {info["ContainersStopped"]}{stopped_container_list}'''
    reply(message, bot, update)


@__command__(
    "restart",
    """Usage: `/restart <CONTAINER>`
Restarts container `CONTAINER`.""")
def command_restart(client: DockerClient,
                    bot: Bot,
                    update: Update,
                    args: List[str]) -> None:
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
    """Usage: `/start`
(Re)initializes the bot's internal state for that user.""")
def command_start(client: DockerClient,
                  bot: Bot,
                  update: Update,
                  args: List[str]) -> None:
    reply(f'Hello {update.message.from_user.first_name} 👋 I am your personal '
          f'docker assistant. Please select a command.',
          bot,
          update,
          reply_markup=ReplyKeyboardMarkup(command_keyboard, selective=True))
