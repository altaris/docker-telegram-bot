"""Various telegram utilities.
"""

import logging
from typing import (
    List,
    Sequence,
    Tuple,
    Union
)

from telegram import (
    Bot,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message
)


def edit_reply(text: str, message: Message, **kwargs) -> Message:
    """Edits a ``telegram.Message``.
    """
    return message.edit_text(
        parse_mode='Markdown',
        text=text,
        **kwargs
    )


def expect_arg_count(arg_count: int,
                     arg_list: List[str],
                     bot: Bot,
                     message: Message) -> bool:
    """Returns True if the argument count is as expected, returns False and
    reports otherwise.
    """
    if len(arg_list) != arg_count:
        reply_error(f'This function expects {arg_count} argument(s).',
                    bot, message)
        return False
    return True


def expect_max_arg_count(max_arg_count: int,
                         arg_list: List[str],
                         bot: Bot,
                         message: Message) -> bool:
    """Returns ``True`` if the argument count is as expected, returns
    ``False`` and reports otherwise.
    """
    if len(arg_list) > max_arg_count:
        reply_error(f'This function expects at most {max_arg_count} '
                    f'argument(s).', bot, message)
        return False
    return True


def expect_min_arg_count(min_arg_count: int,
                         arg_list: List[str],
                         bot: Bot,
                         message: Message) -> bool:
    """Returns ``True`` if the argument count is as expected, returns
    ``False`` and reports otherwise.
    """
    if len(arg_list) < min_arg_count:
        reply_error(f'This function expects at least {min_arg_count} '
                    f'argument(s).', bot, message)
        return False
    return True


def reply(text: str, bot: Bot, message: Message, **kwargs) -> Message:
    """Sends a Markdown message through Telegram.
    """
    return bot.send_message(
        chat_id=message.chat_id,
        parse_mode='Markdown',
        reply_to_message_id=message.message_id,
        text=text,
        **kwargs
    )


def reply_error(text: str, bot: Bot, message: Message) -> Message:
    """Reports an error.
    """
    logging.error('User "%s" raised an error: %s',
                  message.from_user.username, text)
    return reply(f'❌ *ERROR* ❌\n{text}', bot, message)


def reply_warning(text: str, bot: Bot, message: Message) -> Message:
    """Reports an warning.
    """
    logging.warning('User "%s" raised a warning: %s',
                    message.from_user.username, text)
    return reply(f'⚠️ *WARNING* ⚠️\n{text}', bot, message)


def to_inline_keyboard(lst: Sequence[Union[str, Tuple[str, str]]],
                       callback_prefix: str) -> InlineKeyboardMarkup:
    """Creates an inline keyboard from a list of options (str).

    The buttons callback datas are `callback_prefix:button_text`.
    """
    button_list = []  # type: List[InlineKeyboardButton]
    for item in lst:
        if type(item) == str:
            text, code = item, item
        elif type(item) == tuple:
            text, code = item
        button_list += [InlineKeyboardButton(
            text,
            callback_data=f'{callback_prefix}:{code}'
        )]
    return InlineKeyboardMarkup([[button] for button in button_list])
