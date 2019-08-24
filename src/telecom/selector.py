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