import docker
from docker import DockerClient
from docker.models.containers import Container
import logging
from telegram import Bot, Message, ParseMode, Update
from typing import List, Optional


def edit_reply(text: str, message: Message, **kwargs) -> Message:
    return message.edit_text(
        parse_mode='Markdown',
        text=text,
        **kwargs
    )


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


def get_container(client: DockerClient,
                  bot: Bot,
                  update: Update,
                  container_name: str) -> Optional[Container]:
    container = None  # type: Optional[Container]
    try:
        container = client.containers.get(container_name)
    except docker.errors.NotFound:
        reply_error(f'Container \"{container_name}\" not found.', bot, update)
    finally:
        return container


def reply(text: str, bot: Bot, update: Update, **kwargs) -> Message:
    return bot.send_message(
        chat_id=update.message.chat_id,
        parse_mode='Markdown',
        reply_to_message_id=update.message.message_id,
        text=text,
        **kwargs
    )


def reply_error(message: str, bot: Bot, update: Update) -> Message:
    logging.error(f'User "{update.message.from_user.username}" raised an '
                  f'error: {message}')
    return reply(f'❌ *ERROR* ❌\n{message}', bot, update)


def reply_warning(message: str, bot: Bot, update: Update) -> Message:
    logging.warning(f'User "{update.message.from_user.username}" raised a '
                    f'warning: {message}')
    return reply(f'⚠️ *WARNING* ⚠️\n{message}', bot, update)
