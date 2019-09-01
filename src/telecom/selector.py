# -*- coding: utf-8 -*-
"""Defines selectors.

A selector is a class that derives from
:py:class:`telecom.selector.ArgumentSelector` and that implements
:py:meth:`telecom.selector.ArgumentSelector.option_list`. Abstractly, it
represents an inline keyboard to be showed to the user when an argument (having
this selector) is needed.

See :py:meth:`telecom.command.Command.arg`.
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

    COLUMN_COUNT: int = 2
    """Column count of the telegram inline keyboard.

    See implementation of
    :py:meth:`telecom.selector.ArgumentSelector.option_inline_keyboard`"""

    def option_list(self) -> Sequence[Union[str, Tuple[str, str]]]:
        """Implement this.

        This method returns the list of options. An option is either a button
        label, or a tuple formed by a button label and a button code. The code
        is returned through the inline query mechanism of telegram if
        available, otherwise, the label is.

        See `telegram.inlinequery`_.

        .. _telegram.inlinequery: https://python-telegram-bot.readthedocs.io/en/stable/telegram.inlinequery.html
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
        button_layout = []  # type: List[List[InlineKeyboardButton]]
        for idx, button in enumerate(button_list):
            if idx % ArgumentSelector.COLUMN_COUNT == 0:
                button_layout += [[button]]
            else:
                button_layout[-1] += [button]
        return InlineKeyboardMarkup(button_layout)


class YesNoSelector(ArgumentSelector):
    """A simple Yes/No selector
    """

    def option_list(self) -> Sequence[Union[str, Tuple[str, str]]]:
        return [("Yes ✅", "yes"), ("No ❌", "")]
