import logging
from telegram import Bot, ParseMode, Update
from typing import List


def expect_arg_count(arg_count: int,
                     arg_list: List[str],
                     bot: Bot,
                     update: Update) -> bool:
    if len(arg_list) != arg_count:
        reply_error(f'This function expects {arg_count} argument(s).',
                    bot, update)
        return False
    return True


def expect_max_arg_count(max_arg_count: int,
                         arg_list: List[str],
                         bot: Bot,
                         update: Update) -> bool:
    if len(arg_list) > max_arg_count:
        reply_error(f'This function expects at most {max_arg_count} '
                    f'argument(s).', bot, update)
        return False
    return True


def expect_min_arg_count(min_arg_count: int,
                         arg_list: List[str],
                         bot: Bot,
                         update: Update) -> bool:
    if len(arg_list) < min_arg_count:
        reply_error(f'This function expects at least {min_arg_count} '
                    f'argument(s).', bot, update)
        return False
    return True


def reply(message: str, bot: Bot, update: Update, **kwargs) -> None:
    bot.send_message(
        chat_id=update.message.chat_id,
        parse_mode='Markdown',
        reply_to_message_id=update.message.message_id,
        text=message,
        **kwargs
    )


def reply_error(message: str, bot: Bot, update: Update) -> None:
    reply(f'❌ *ERROR* ❌\n{message}', bot, update)
    logging.error(f'User "{update.message.from_user.username}" raised an '
                  f'error: {message}')


def reply_warning(message: str, bot: Bot, update: Update) -> None:
    reply(f'⚠️ *WARNING* ⚠️\n{message}', bot, update)
    logging.warning(f'User "{update.message.from_user.username}" raised a '
                    f'warning: {message}')
