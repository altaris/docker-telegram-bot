# -*- coding: utf-8 -*-
"""Implentation of builtin command `/help`.
"""

from typing import (
    Dict,
    Optional,
    Sequence,
    Tuple,
    Union
)

from telecom.command import (
    Command
)
from telecom.selector import (
    ArgumentSelector
)


class CommandSelector(ArgumentSelector):
    """Selects a command name among all registered commands.
    """

    def option_list(self) -> Sequence[Union[str, Tuple[str, str]]]:
        return [
            ("/" + command_name, command_name)
            for command_name in Help.HELP_DICT
        ]


class Help(Command):
    """Implentation of builtin command `/help`.
    """

    __HELP__ = """▪️ Usage: `/help COMMAND`
Displays help message of a command."""

    HELP_DICT: Dict[str, Optional[str]] = {}
    """Dictionary that maps a command name to its help text."""

    def main(self) -> None:
        command_name = self.arg(
            "0",
            CommandSelector(),
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
