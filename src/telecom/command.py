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
    Optional
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

from telecom.selector import (
    ArgumentSelector,
    YesNoSelector
)


COMMANDS = {}  # type: Dict[str, Command]
COMMANDS_HELP = {}  # type: Dict[str, Optional[str]]
COMMAND_KEYBOARD = ReplyKeyboardMarkup([
    ["/info", "/help"],
    ["/start", "/stop", "/restart"],
    ["/pause", "/unpause"]
])  # type: ReplyKeyboardMarkup


class NotEnoughArguments(Exception):
    pass


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
        self._args_dict[arg_name] = arg_value


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
        Command.CALL_STORE[call_idx](bot, update)
    else:
        logging.error("Bad call index %s", call_idx)


class SimpleCommand(Command):

    def main(self) -> None:
        answer = self.arg("answer", YesNoSelector())
        self.reply("You said: " + answer)


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
