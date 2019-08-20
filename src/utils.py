import logging
from telegram import Bot, ParseMode, Update
from typing import List


def assert_arg_count(arg_count: int,
                     arg_list: List[str],
                     bot: Bot,
                     update: Update) -> bool:
    if len(arg_list) != arg_count:
        reply_error(f'This function expects {arg_count} argument(s).',
                    bot, update)
        return False
    return True


def reply(message: str, bot: Bot, update: Update, **kwargs) -> None:
    bot.send_message(
        chat_id=update.message.chat_id,
        parse_mode=ParseMode.MARKDOWN,
        reply_to_message_id=update.message.message_id,
        text=message,
        **kwargs
    )


def reply_error(message: str, bot: Bot, update: Update) -> None:
    reply(f'❌ **ERROR** ❌\n{message}', bot, update)
    logging.error(f'User "{update.message.from_user.username}" raised an '
                  f'error: {message}')


def reply_warning(message: str, bot: Bot, update: Update) -> None:
    reply(f'⚠️ **WARNING** ⚠️\n{message}', bot, update)
    logging.warning(f'User "{update.message.from_user.username}" raised a '
                    f'warning: {message}')
