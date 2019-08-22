"""Implementation of the commands supported by of the bot.

A command is a callable that has type ``commands.Command``. It is expected to
be implemented in a ``cmd_commandname.py`` file as function ``main``. Further,
that ``cmd_commandname`` must have globals ``NAME`` for the command name, and
``HELP`` for the help text.
"""

import functools
import importlib
import logging
import os
import re
from typing import (
    Callable,
    Dict,
    List,
    Optional,
    Union
)

from docker import (
    DockerClient
)
import telegram
import telegram.ext
from telegram import (
    Bot,
    KeyboardButton,
    Update
)

from telegram_utils import (
    expect_arg_count,
    reply,
    reply_error
)

Command = Callable[[DockerClient, Bot, Update, List[str]], None]


COMMANDS = {}  # type: Dict[str, Command]
COMMANDS_HELP = {}  # type: Dict[str, Optional[str]]
COMMAND_KEYBOARD = [
    ["/info", "/help"],
    ["/start", "/stop", "/restart"]
]  # type: List[List[Union[str, KeyboardButton]]]


TelegramError = Union[telegram.error.TelegramError,
                      telegram.error.NetworkError]


def command_help(client: DockerClient,
                 bot: Bot,
                 update: Update,
                 args: List[str]) -> None:
    """Implentation of builtin command `/help`.
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
        reply(f"🆘 *Help for command `{command_name}`* 🆘\n{command_doc}",
              bot, update)


def error_callback(bot: telegram.Bot,
                   update: telegram.Update,
                   error: TelegramError) -> None:
    # pylint: disable=line-too-long
    """Custom telegram error callback.

    See https://python-telegram-bot.readthedocs.io/en/stable/telegram.ext.dispatcher.html?highlight=error%20callback#telegram.ext.Dispatcher.add_error_handler
    """
    # pylint: disable=unused-argument
    try:
        raise error
    except telegram.error.Unauthorized as err:
        logging.error("Unauthorized: %s", str(err))
    except telegram.error.BadRequest as err:
        logging.error("BadRequest: %s", str(err))
    except telegram.error.TimedOut as err:
        logging.error("TimedOut: %s", str(err))
    except telegram.error.NetworkError as err:
        logging.error("NetworkError: %s", str(err))
    except telegram.error.ChatMigrated as err:
        logging.error("ChatMigrated: %s", str(err))
    except telegram.error.TelegramError as err:
        logging.error("TelegramError: %s", str(err))


def load_command(command_name: str,
                 help_text: str,
                 callback: Command,
                 command_filter: telegram.ext.filters.BaseFilter,
                 docker_client: DockerClient,
                 dispatcher: telegram.ext.Dispatcher) -> None:
    """Loads a specific command.
    """
    logging.debug("Loading command %s", command_name)
    COMMANDS[command_name] = callback
    COMMANDS_HELP[command_name] = help_text
    dispatcher.add_handler(telegram.ext.CommandHandler(
        command_name,
        functools.partial(callback, docker_client),
        filters=command_filter,
        pass_args=True))


def load_commands(updater: telegram.ext.Updater,
                  docker_client: DockerClient,
                  authorized_users: List[int]) -> None:
    """Loads all commands.

    Recall that a command is the ``main`` function of a ``cmd_commandname``
    Python module.
    """
    # pyling: disable=global-statement
    global COMMANDS

    current_dir = os.path.dirname(os.path.realpath(__file__))
    command_module_files = [
        basename for basename in os.listdir(current_dir)
        if os.path.isfile(os.path.join(current_dir, basename))
        and re.match(r'cmd_\w+\.py', basename)
    ]

    dispatcher = updater.dispatcher
    dispatcher.add_error_handler(error_callback)
    authorized_users_filter =                                   \
        telegram.ext.filters.Filters.user(authorized_users) |   \
        telegram.ext.filters.Filters.text

    for command_module_file in command_module_files:
        command_module = command_module_file[:-3]
        module = importlib.import_module(command_module)
        load_command(module.NAME, module.HELP, module.main,  # type: ignore
                     authorized_users_filter, docker_client, dispatcher)
    load_command(
        "help",
        "Usage `/help <COMMAND>` (builtin command)\nDisplays help message "
        "about `COMMAND` if available.",
        command_help,
        authorized_users_filter,
        docker_client,
        dispatcher)
