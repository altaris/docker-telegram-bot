# -*- coding: utf-8 -*-
"""Defines selectors.

A selector is a class that derives from ``telecom.selector.ArgumentSelector``
and that implements ``telecom.selector.ArgumentSelector.option_list``.
Abstractly, it represents an inline keyboard to be showed to the user when an
argument (having this selector) is needed.

See ``telecom.command.Command.arg``.
"""

from typing import (
    List,
    Sequence,
    Tuple,
    Union
)

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup
)


class ArgumentSelector:
    """An abstract argument selector.
    """

    def option_list(self) -> Sequence[Union[str, Tuple[str, str]]]:
        """Implement this.
        """
        raise NotImplementedError

    def option_inline_keyboard(self,
                               callback_prefix: str) -> InlineKeyboardMarkup:
        """Creates a inline keyboard out of the options provided by this
        selector.
        """
        button_list = []  # type: List[InlineKeyboardButton]
        for item in self.option_list():
            if isinstance(item, str):
                text, code = item, item
            elif isinstance(item, tuple):
                text, code = item
            button_list += [InlineKeyboardButton(
                text,
                callback_data=f'{callback_prefix}:{code}'
            )]
        return InlineKeyboardMarkup([[button] for button in button_list])


class YesNoSelector(ArgumentSelector):
    """A simple Yes/No selector
    """

    def option_list(self) -> Sequence[Union[str, Tuple[str, str]]]:
        return ["Yes", ("No", "")]
