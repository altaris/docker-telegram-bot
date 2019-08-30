# -*- coding: utf-8 -*-
"""Implementation of command related abstract classes and functions.
"""

from enum import (
    auto,
    IntEnum
)
import functools
import logging
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

from telegram import (
    Bot,
    Message,
    ParseMode,
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


class NotEnoughArguments(Exception):
    """This exception is raised when a command doesn't have enough argument.

    It is caught by ``Command.__call__``, so in practice, it just interrupts
    the execution flow.
    """


class Command:
    """This class represent an abstract command that can be issued over
    telegram.

    Simply derive this class and implement ``telecom.Command.main``. A help
    message can be stored in class static member ``telecom.Command.__HELP__``.

    Attributes:
        PENDING_COMMANDS: Global dict of pending commands.
        PENDING_COMMANDS_COUNTER: A global counter that is incremented each
            a new pending command is added to PENDING_COMMANDS
        GLOBAL_HOOKS: A global dict containing all hooks.
        __HELP__: Help text of that command.
        _args_dict: Argument dict.
        _bot: Telegram bot that called this command.
        _first_call: Wether this is the first time this command instance is
            called.
        _message: Either the user message that called this command, or the last
            message the command sent.
        _pending_idx: Key of this command in PENDING_COMMANDS, or ``None`` if
            the command is not pending.
    """

    class HookType(IntEnum):
        """Hook types.

        A hook is a function called at certain points of the execution of a
        command. They are added using ``telecom.command.add_command_hook``.
        There can be multiple functions per hook.

        The currently supported hook types are:
            * `ON_CALLED_FOR_THE_FIRST_TIME`: when the command instance is
              called for the first time;
            * `ON_CALLED_NOT_FOR_THE_FIRST_TIME`: when the command instance is
               called but not for the first time;
            * `ON_CREATED`: when the command instance is created;
            * `ON_FINISHED`: when the command instance finishes execution
               NORMALLY;
            * `ON_NOT_ENOUGH_ARGUMENTS`: when the execution of the command is
              interrupted because of missing arguments;
            * `ON_RAISED_EXCEPTION`: when an exception (other than
              ``telecom.command.NotEnoughArguments``) is raised.
        """
        ON_CALLED_FOR_THE_FIRST_TIME = auto()
        ON_CALLED_NOT_FOR_THE_FIRST_TIME = auto()
        ON_CREATED = auto()
        ON_FINISHED = auto()
        ON_NOT_ENOUGH_ARGUMENTS = auto()
        ON_RAISED_EXCEPTION = auto()


    PENDING_COMMANDS = {}  # type: Dict[str, Command]
    PENDING_COMMANDS_COUNTER: int = 0
    GLOBAL_HOOKS = {}  # type: Dict[HookType, Sequence[Callable[[Command], None]]]

    __HELP__: Optional[str] = None

    _args_dict: Dict[str, Any]
    _bot: Bot
    _first_call: bool
    _message: Message
    _pending_idx: Optional[str]

    def __call__(self,
                 bot: Bot,
                 update: Update,
                 args: List[str],
                 **kwargs) -> None:
        """The command is called through this method by the telegram dispatcher.

        Do not reimplement this. It calls hooks and catches
        ``telecom.command.NotEnoughArguments`` exceptions.
        """
        if self._first_call:
            self._bot = bot
            self._first_call = False
            self._message = update.message
            self.call_hooks(Command.HookType.ON_CALLED_FOR_THE_FIRST_TIME)
        else:
            self.call_hooks(Command.HookType.ON_CALLED_NOT_FOR_THE_FIRST_TIME)

        kwargs_dict = {**kwargs}
        kwargs_dict.update({
            str(idx): val for idx, val in enumerate(args)
        })
        kwargs_dict.update(self._args_dict)
        self._args_dict = kwargs_dict

        try:
            self.main()
        except NotEnoughArguments:
            self.call_hooks(Command.HookType.ON_NOT_ENOUGH_ARGUMENTS)
        except:
            self.call_hooks(Command.HookType.ON_RAISED_EXCEPTION)
            raise
        else:
            if self._pending_idx in Command.PENDING_COMMANDS:
                Command.PENDING_COMMANDS.pop(self._pending_idx)
            self.call_hooks(Command.HookType.ON_FINISHED)

    def __init__(self):
        self._args_dict = {}
        self._pending_idx = None
        self._first_call = True
        self.call_hooks(Command.HookType.ON_CREATED)

    def arg(self,
            arg_name: str,
            selector: ArgumentSelector,
            text: str = "Select an option:") -> Any:
        """This function returns the value of an argument.

        If the argument is not available, the selector displays an inline
        keyboard, and the command instance raises a
        ``telecom.command.NotEnoughArguments`` exception instance so as to be
        stored in ``telecom.Command.PENDING_COMMANDS`` (see
        ``telecom.command.Command.__call__``) waiting to be called again with
        the missing argument.
        """
        if arg_name in self._args_dict:
            return self._args_dict[arg_name]
        if not self._pending_idx:
            Command.PENDING_COMMANDS_COUNTER += 1
            self._pending_idx = str(Command.PENDING_COMMANDS_COUNTER)
            Command.PENDING_COMMANDS[self._pending_idx] = self
        self.reply(
            text,
            reply_markup=selector.option_inline_keyboard(
                f'{self._pending_idx}:{arg_name}'
            )
        )
        raise NotEnoughArguments

    def call_hooks(self, hook_type: HookType):
        """Calls all hooks of a given type.

        Hooks are called in the order they have been added using
        ``telecom.command.add_command_hook``.
        """
        for hook in Command.GLOBAL_HOOKS.get(hook_type, []):
            hook(self)

    def delete_reply(self):
        """Deletes the last message sent by this command.
        """
        self._bot.delete_message(self._message.chat_id,
                                 self._message.message_id)

    def edit_reply(self, text: str, **kwargs) -> None:
        """Edits the last message sent by this command.
        """
        self._message = self._message.edit_text(
            parse_mode=ParseMode.MARKDOWN,
            text=text,
            **kwargs
        )

    def main(self) -> None:
        """Main code of the command.

        This function may be executed multiple times even if the telegram user
        invokes it once. This is due to the execution flow breaking
        ``telecom.command.NotEnoughArgument`` that is raised when missing
        arguments are requested.
        """
        raise NotImplementedError

    def reply(self, text: str, **kwargs) -> None:
        """Sends a markdown message through telegram.
        """
        self._message = self._bot.send_message(
            chat_id=self._message.chat_id,
            parse_mode=ParseMode.MARKDOWN,
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
        command_name = self.arg(
            "0",
            Help.CommandSelector(),
            "Choose a command:"
        )
        if command_name not in Help.HELP_DICT:
            self.reply_error(f'Command `{command_name}` not found.')
            return
        command_doc = Help.HELP_DICT.get(command_name, None)
        if command_doc is None:
            self.reply(f'No help available for command `{command_name}`.')
        else:
            self.reply(
                f'🆘 *Help for command* `{command_name}` 🆘\n{command_doc}'
            )


def add_command_hook(hook_type: Command.HookType,
                     hook: Callable[[Command], None]) -> None:
    """Adds a global command hook.
    """
    Command.GLOBAL_HOOKS[hook_type] = [hook] + \
        list(Command.GLOBAL_HOOKS.get(hook_type, []))


def inline_query_handler(bot: Bot, update: Update) -> None:
    """Global inline query handler.
    """
    data = update.callback_query.data.split(":")
    logging.debug("Received callback query %s", str(data))
    call_idx = data[0]
    arg_name = data[1]
    arg_value = data[2]
    if call_idx in Command.PENDING_COMMANDS:
        Command.PENDING_COMMANDS[call_idx].set_arg(arg_name, arg_value)
        Command.PENDING_COMMANDS[call_idx](bot, update, [])
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
