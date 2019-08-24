# -*- coding: utf-8 -*-
"""Implementation of the commands supported by of the bot.

A command is a callable that has type ``commands.Command``. It is expected to
be implemented in a ``cmd_commandname.py`` file as function ``main``. Further,
that ``cmd_commandname`` must have globals ``NAME`` for the command name, and
``HELP`` for the help text.
"""

import functools
import logging
from typing import (
    Any,
    Dict,
    List,
    Optional,
    Sequence,
    Tuple,
    Union
)

from telegram import (
    Bot,
    Message,
    ReplyKeyboardMarkup,
    Update
)
from telegram.ext import (
    CommandHandler,
    Dispatcher
)
from telegram.ext.filters import (
    Filters
)

from telecom.selector import (
    ArgumentSelector
)


COMMANDS = {}  # type: Dict[str, Command]
COMMAND_KEYBOARD = ReplyKeyboardMarkup([
    ["/info", "/help"],
    ["/start", "/stop", "/restart"],
    ["/pause", "/unpause"]
])  # type: ReplyKeyboardMarkup


class NotEnoughArguments(Exception):
    """This exception is raised when a command doesn't have enough argument.

    It is caught by `Command.__call__`, so in practice, it just interrupts the
    execution flow.
    """


class Command:
    """This class represent an abstract command that can be issued over
    telegram.

    Simply derive this class and implement `telecom.Command.main`. A help
    message can be stored in class static member `telecom.Command.__HELP__`.
    """

    CALL_STORE = {}  # type: Dict[str, Command]
    CALL_COUNTER: int = 0

    __HELP__: Optional[str] = None

    _args_dict: Dict[str, Any] = {}
    _bot: Bot
    _call_store_idx: Optional[str] = None
    _first_call: bool = True
    _message: Message

    def __call__(self,
                 bot: Bot,
                 update: Update,
                 args: List[str],
                 **kwargs) -> None:
        """The command is called through this method.

        Do not reimplement this.
        """
        if self._first_call:
            self._bot = bot
            self._message = update.message
            self._first_call = False
        for key, val in kwargs.items():
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
        """This function returns the value of an argument.

        If the argument is not available, the selector displays an inline
        keyboard, and the command instance is stored in
        `telecom.Command.CALL_STORE` waiting to be called again with the
        missing argument.
        """
        if arg_name in self._args_dict:
            return self._args_dict[arg_name]
        else:
            if not self._call_store_idx:
                Command.CALL_COUNTER += 1
                self._call_store_idx = str(Command.CALL_COUNTER)
                Command.CALL_STORE[self._call_store_idx] = self
            self.reply(
                "Select an option:",
                reply_markup=selector.option_inline_keyboard(
                    f'{self._call_store_idx}:{arg_name}'
                )
            )
            raise NotEnoughArguments

    def edit_reply(self, text: str, **kwargs) -> None:
        """Edits the last message sent by this command.
        """
        self._message = self._message.edit_text(
            parse_mode='Markdown',
            text=text,
            **kwargs
        )

    def main(self) -> None:
        """Implement this method.
        """
        raise NotImplementedError

    def reply(self, text: str, **kwargs) -> None:
        """Sends a Markdown message through Telegram.
        """
        self._message = self._bot.send_message(
            chat_id=self._message.chat_id,
            parse_mode='Markdown',
            reply_to_message_id=self._message.message_id,
            text=text,
            **kwargs
        )

    def reply_error(self, text: str) -> None:
        """Reports an error.
        """
        logging.error('User "%s" raised an error: %s',
                      self._message.from_user.username, text)
        self.reply(f'❌ *ERROR* ❌\n{text}')


    def reply_warning(self, text: str) -> None:
        """Reports an warning.
        """
        logging.warning('User "%s" raised a warning: %s',
                        self._message.from_user.username, text)
        self.reply(f'⚠️ *WARNING* ⚠️\n{text}')

    def set_arg(self, arg_name: str, arg_value: Any) -> None:
        """Sets the value of an argument.
        """
        self._args_dict[arg_name] = arg_value



class Help(Command):
    """Implentation of builtin command `/help`.
    """

    __HELP__ = """▪️ Usage: `/help COMMAND`
Displays help message of `COMMAND`."""

    HELP_DICT: Dict[str, Optional[str]] = {}

    class CommandSelector(ArgumentSelector):
        """Selects a command name among all registered commands.
        """

        def option_list(self) -> Sequence[Union[str, Tuple[str, str]]]:
            return [
                ("/" + command_name, command_name)
                for command_name in Help.HELP_DICT
            ]

    def main(self) -> None:
        command_name = self.arg("command_name", Help.CommandSelector())
        if command_name not in Help.HELP_DICT:
            self.reply_error(f'Command `{command_name}` not found.')
            return
        command_doc = Help.HELP_DICT.get(command_name, None)
        if command_doc is None:
            self.reply(f'No help available for command `{command_name}`.')
        else:
            self.reply(
                f'🆘 *Help for command `{command_name}`* 🆘\n{command_doc}'
            )


def inline_query_handler(bot: Bot, update: Update) -> None:
    """Global inline query handler.
    """
    data = update.callback_query.data.split(":")
    logging.debug("Received callback query %s", str(data))
    call_idx = data[0]
    arg_name = data[1]
    arg_value = data[2]
    if call_idx in Command.CALL_STORE:
        Command.CALL_STORE[call_idx].set_arg(arg_name, arg_value)
        Command.CALL_STORE[call_idx](bot, update, [])
    else:
        logging.error("Bad call index %s", call_idx)


def register_command(dispatcher: Dispatcher,
                     command_name: str,
                     command_class,
                     **kwargs) -> None:
    """Registers a new command.

    Args:
        dispatcher (telegram.ext.Dispatcher): Telegram dispatcher
        command_name (str): Command name
        command_class (type): Class where the command is implemented
        defaults (dict): Defaults arguments to be passed to the instances of
                         that command
        authorized_users: List of users authorized to call this command; if
                          none provided, all users are authorized
    """
    def factory(*args, **kwargs):
        cmd = command_class()
        cmd(*args, **kwargs)

    logging.debug("Registering command %s", command_name)

    COMMANDS[command_name] = command_class
    Help.HELP_DICT[command_name] = command_class.__HELP__

    authorized_users = kwargs.get("authorized_users", [])
    command_filters = Filters.command
    if authorized_users:
        command_filters &= Filters.user(authorized_users)

    dispatcher.add_handler(
        CommandHandler(
            command_name,
            functools.partial(factory, **(kwargs.get("defaults", {}))),
            pass_args=True,
            filters=command_filters
        )
    )


def register_help_command(dispatcher: Dispatcher) -> None:
    """Registers builtin help command.

    See ``telecom.cmd_help.Help``.
    """
    register_command(
        dispatcher,
        "help",
        Help
    )
