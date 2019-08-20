from docker import DockerClient
from telegram import Bot, KeyboardButton, ParseMode, ReplyKeyboardMarkup
from telegram.ext import Updater
from typing import Callable, Dict, List, Optional, Union


from utils import *


Command = Callable[[DockerClient, Bot, Updater, List[str]], None]


commands = {}  # type: Dict[str, Command]
command_keyboard = [
    [
        "/start", "/info", "/help"
    ]
]  # type: List[List[Union[str, KeyboardButton]]]


def _command(name: Optional[str] = None):
    """Decorator for command callbacks.

    A command callback has type commands.Command.
    """
    def decorator(cmd: Command):
        if name:
            global commands
            commands[name] = cmd
        return cmd
    return decorator


@_command("help")
def command_help(client: DockerClient,
                 bot: Bot,
                 update: Updater,
                 args: List[str]) -> None:
    if not assert_arg_count(1, args, bot, update):
        return
    command_name = args[0]
    if command_name not in commands:
        reply_error(f'Command `{command_name}` not found.', bot, update)
        return
    command_doc = commands[command_name].__doc__
    if command_doc is None:
        reply(f'No help available for command `{command_name}` ☹️',
              bot, update)
    else:
        reply(f'🆘 **Help for command `{command_name}`** 🆘\n{command_doc}',
              bot, update)


@_command("info")
def command_info(client: DockerClient,
                 bot: Bot,
                 update: Updater,
                 args: List[str]) -> None:
    """Provides global informations about the current docker daemon."""
    info = client.info()
    message = f'''**Docker status** 🐳⚙️
▪️ Docker version: {info["ServerVersion"]}
▪️ Memory: {info["MemTotal"]}
▪️ Running containers: {info["ContainersRunning"]}
▪️ Paused containers: {info["ContainersPaused"]}
▪️ Stopped containers: {info["ContainersStopped"]}'''
    reply(message, bot, update)


@_command("start")
def command_start(client: DockerClient,
                  bot: Bot,
                  update: Updater,
                  args: List[str]) -> None:
    """Reinitialize the bot's internal state for that user."""
    reply(f'Hello {update.message.from_user.first_name} 👋 I am your personal '
          f'docker assistant. Please select a command.',
          bot,
          update,
          reply_markup=ReplyKeyboardMarkup(command_keyboard, selective=True))
