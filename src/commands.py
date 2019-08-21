import docker
from docker import DockerClient
import logging
from telegram import Bot, KeyboardButton, ParseMode, ReplyKeyboardMarkup
from telegram.ext import Updater
from typing import Callable, Dict, List, Optional, Union


from utils import *


Command = Callable[[DockerClient, Bot, Updater, List[str]], None]


commands = {}  # type: Dict[str, Command]
commands_help = {}  # type: Dict[str, str]
command_keyboard = [
    [
        "/start", "/info", "/help"
    ]
]  # type: List[List[Union[str, KeyboardButton]]]


def _command(name: Optional[str] = None, help_msg: str = ""):
    """Decorator for command callbacks.

    A command has type commands.Command. This decorator wraps it to catch and
    report docker.errors.APIError exceptions.
    """
    def decorator(cmd: Command):
        def wrapper(client: DockerClient,
                    bot: Bot,
                    update: Updater,
                    args: List[str]) -> None:
            try:
                cmd(client, bot, update, args)
            except docker.errors.APIError as e:
                reply_error(f'Docker daemon raised an API error: {str(e)}',
                            bot, update)
        if name:
            global commands
            global commands_help
            commands[name] = cmd
            commands_help[name] = help_msg
        return cmd
    return decorator


@_command(
    "help",
    """Usage `/help <COMMAND>`
Displays help message about `COMMAND` if available.""")
def command_help(client: DockerClient,
                 bot: Bot,
                 update: Updater,
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


@_command(
    "info",
    """Usage: `/info [CONTAINER]`
Provides global informations about the current docker daemon, or about `CONTAINER`, if specified.""")
def command_info(client: DockerClient,
                 bot: Bot,
                 update: Updater,
                 args: List[str]) -> None:
    if not expect_max_arg_count(1, args, bot, update):
        return
    if len(args) == 0:
        reply(command_info_docker(client), bot, update)
    else:
        container_name = args[0]
        try:
            reply(command_info_container(client, container_name), bot, update)
        except docker.errors.NotFound:
            reply_error(f'Container \"{container_name}\" not found.', bot,
                        update)


def command_info_container(client: DockerClient, container_name: str) -> str:
    c = client.containers.get(container_name)
    return f'''*Container `{c.short_id} {c.name}`:*
️️️️️️️▪️ Image: {c.image}
️️️️️️️▪️ Status: {c.status}
️️️️️️️▪️ Labels: {c.labels}'''


def command_info_docker(client: DockerClient) -> str:
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
    return f'''*Docker status* 🐳⚙️
▪️ Docker version: {info["ServerVersion"]}
▪️ Memory: {info["MemTotal"]}
▪️ Running containers: {info["ContainersRunning"]}{running_container_list}
▪️ Paused containers: {info["ContainersPaused"]}{paused_container_list}
▪️ Stopped containers: {info["ContainersStopped"]}{stopped_container_list}'''


@_command(
    "start",
    """Usage: `/start`
(Re)initializes the bot's internal state for that user.""")
def command_start(client: DockerClient,
                  bot: Bot,
                  update: Updater,
                  args: List[str]) -> None:
    reply(f'Hello {update.message.from_user.first_name} 👋 I am your personal '
          f'docker assistant. Please select a command.',
          bot,
          update,
          reply_markup=ReplyKeyboardMarkup(command_keyboard, selective=True))
