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

    A command callback has type commands.Command.
    """
    def decorator(cmd: Command):
        if name:
            global commands
            global commands_help
            commands[name] = cmd
            commands_help[name] = help_msg
        return cmd
    return decorator


@_command(
    "help",
    """Usage `/help COMMAND`
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
        info = client.info()
        message = f'''*Docker status* 🐳⚙️
▪️ Docker version: {info["ServerVersion"]}
▪️ Memory: {info["MemTotal"]}
▪️ Running containers: {info["ContainersRunning"]}
▪️ Paused containers: {info["ContainersPaused"]}
▪️ Stopped containers: {info["ContainersStopped"]}'''
        reply(message, bot, update)
    else:
        container_id = args[0]
        logging.debug(container_id)
        try:
            c = client.containers.get(container_id)
            message = f'''*Container `{c.short_id} {c.name}`:*
️️️️️️️️▪️ Image: {c.image}
️️️️️️️️▪️ Status: {c.status}
️️️️️️️️▪️ Labels: {c.labels}'''
            reply(message, bot, update)
        except docker.errors.NotFound:
            reply_error(f'Container \"{container_id}\" not found.', bot,
                        update)
        except docker.errors.APIError as e:
            reply_error(f'Docker daemon error: {str(e)}', bot, update)


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
