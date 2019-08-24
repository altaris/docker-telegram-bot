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
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Sequence,
    Tuple,
    Union
)

import docker.errors
from docker import (
    DockerClient
)
import telegram
import telegram.ext
from telegram import (
    Bot,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    ReplyKeyboardMarkup,
    Update
)

from telegram_utils import (
    reply,
    reply_error,
    to_inline_keyboard
)

# Command = Callable[[DockerClient, Bot, Message, List[str]], None]

# Command = Callable[
#     [
#         Bot,                # Telegram bot
#         Message,            # Telegram message
#         Dict[str, Any]      # Arguments
#     ],
#     None
# ]


COMMANDS = {}  # type: Dict[str, Command]
COMMANDS_HELP = {}  # type: Dict[str, Optional[str]]
COMMAND_KEYBOARD = ReplyKeyboardMarkup([
    ["/info", "/help"],
    ["/start", "/stop", "/restart"],
    ["/pause", "/unpause"]
])  # type: ReplyKeyboardMarkup


TelegramError = Union[telegram.error.TelegramError,
                      telegram.error.NetworkError]


class NotEnoughArguments(Exception):
    pass


class ArgumentSelector:

    def option_list(self) -> Sequence[Union[str, Tuple[str, str]]]:
        return []

    def option_inline_keyboard(self,
                               callback_prefix: str) -> InlineKeyboardMarkup:
        button_list = []  # type: List[InlineKeyboardButton]
        for item in self.option_list():
            if type(item) == str:
                text, code = item, item
            elif type(item) == tuple:
                text, code = item
            button_list += [InlineKeyboardButton(
                text,
                callback_data=f'{callback_prefix}:{code}'
            )]
        return InlineKeyboardMarkup([[button] for button in button_list])


class YesNoSelector(ArgumentSelector):

    def option_list(self) -> Sequence[Union[str, Tuple[str, str]]]:
        return ["Yes", ("No", "")]


class Command:

    CALL_STORE = {}  # type: Dict[str, Command]
    CALL_COUNTER = 0

    _args_dict: Dict[str, Any] = {}
    _bot: Bot
    _call_store_idx: Optional[str] = None
    _first_call: bool = True
    _message: Message

    def __call__(self,
                 bot: Bot,
                 update: Update,
                 args: List[str] = [],
                 **kwargs) -> None:
        if self._first_call:
            self._bot = bot
            self._message = update.message
            self._first_call = False
        for key, val in kwargs.items():
            print(key)
            print(val)
            if key not in self._args_dict:
                self._args_dict[key] = val
        for idx, val in enumerate(args):
            self._args_dict[str(idx)] = val
        try:
            self.main()
        except NotEnoughArguments:
            pass
        else:
            # TODO: If another exception arises, cleanup code isn't executed
            if self._call_store_idx in Command.CALL_STORE:
                Command.CALL_STORE.pop(self._call_store_idx)

    def __init__(self):
        self._args_dict = {}
        self._call_store_idx = None
        self._first_call = True

    def arg(self,
            arg_name: str,
            selector: ArgumentSelector) -> Any:
        if arg_name in self._args_dict:
            return self._args_dict[arg_name]
        else:
            if not self._call_store_idx:
                Command.CALL_COUNTER += 1
                self._call_store_idx = str(Command.CALL_COUNTER)
                Command.CALL_STORE[self._call_store_idx] = self
            reply(
                "Select an option:",
                self._bot,
                self._message,
                reply_markup=selector.option_inline_keyboard(
                    f'{self._call_store_idx}:{arg_name}'
                )
            )
            raise NotEnoughArguments

    def main(self) -> None:
        raise NotImplementedError


def inline_query_handler(bot: Bot, update: Update) -> None:
    """Global inline query handler.
    """
    data = update.callback_query.data.split(":")
    logging.info("Received callback query %s", str(data))
    call_idx = data[0]
    arg_name = data[1]
    arg_value = data[2]
    if call_idx in Command.CALL_STORE:
        Command.CALL_STORE[call_idx]._args_dict[arg_name] = arg_value
        Command.CALL_STORE[call_idx](bot, update)
    else:
        logging.error("Bad call index %s", call_idx)


class SimpleCommand(Command):

    def main(self) -> None:
        print(self._args_dict)
        answer = self.arg("answer", YesNoSelector())
        reply(
            "You said: " + answer,
            self._bot,
            self._message
        )


# def command_help(bot: Bot,
#                  message: Message,
#                  args: Dict[str, Any]) -> None:
#     """Implentation of builtin command `/help`.
#     """
#     # pylint: disable=unused-argument
#     if not args:
#         reply(
#             "Select an option",
#             bot,
#             message,
#             reply_markup=to_inline_keyboard(list(COMMANDS.keys()), "help")
#         )
#         return
#     command_name = args[0]
#     if command_name not in COMMANDS:
#         reply_error(f'Command `{command_name}` not found.', bot, message)
#         return
#     command_doc = COMMANDS_HELP.get(command_name, None)
#     if command_doc is None:
#         reply(f'No help available for command `{command_name}`.',
#               bot, message, reply_markup=COMMAND_KEYBOARD)
#     else:
#         reply(f"🆘 *Help for command `{command_name}`* 🆘\n{command_doc}",
#               bot, message, reply_markup=COMMAND_KEYBOARD)


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


def register_command(command_name: str,
                     command_class,
                     dispatcher: telegram.ext.Dispatcher,
                     **defaults) -> None:
    def factory(*args, **kwargs):
        cmd = command_class()
        cmd(*args, **kwargs)
    logging.debug("Registering command %s", command_name)
    global COMMANDS
    COMMANDS[command_name] = command_class
    dispatcher.add_handler(telegram.ext.CommandHandler(
        command_name,
        functools.partial(factory, **defaults),
        pass_args=True
    ))


def load_commands(updater: telegram.ext.Updater,
                  docker_client: DockerClient,
                  authorized_users: List[int]) -> None:
    """Loads all commands.

    Recall that a command is the ``main`` function of a ``cmd_commandname``
    Python module.
    """
    dispatcher = updater.dispatcher
    dispatcher.add_error_handler(error_callback)
    dispatcher.add_handler(telegram.ext.CallbackQueryHandler(
        inline_query_handler
    ))
    register_command("test", SimpleCommand, dispatcher)
    # current_dir = os.path.dirname(os.path.realpath(__file__))
    # command_module_files = [
    #     basename for basename in os.listdir(current_dir)
    #     if os.path.isfile(os.path.join(current_dir, basename))
    #     and re.match(r'cmd_\w+\.py', basename)
    # ]


    # dispatcher.add_handler(telegram.ext.CallbackQueryHandler(
    #     functools.partial(inline_query_handler, docker_client)
    # ))

    # authorized_users_filter =                                   \
    #     telegram.ext.filters.Filters.user(authorized_users) |   \
    #     telegram.ext.filters.Filters.text

    # for command_module_file in command_module_files:
    #     command_module = command_module_file[:-3]
    #     module = importlib.import_module(command_module)
    #     load_command(module.NAME, module.HELP, module.main,  # type: ignore
    #                  authorized_users_filter, docker_client, dispatcher)
    # load_command(
    #     "help",
    #     "Usage `/help <COMMAND>` (builtin command)\nDisplays help message "
    #     "about `COMMAND` if available.",
    #     command_help,
    #     authorized_users_filter,
    #     docker_client,
    #     dispatcher)
