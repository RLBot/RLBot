import flatbuffers
import multiprocessing
import queue
from threading import Thread

from rlbot.messages.flat import QuickChat
from rlbot.messages.flat import QuickChatSelection
from rlbot.utils.logging_utils import get_logger

from rlbot.utils.structures.utils import create_enum_object


"""
Look for quick chats from here:
https://github.com/RLBot/RLBot/blob/master/src/main/flatbuffers/rlbot.fbs
"""
QuickChats = create_enum_object([chat for chat in dir(QuickChatSelection.QuickChatSelection)
                                 if not chat.startswith('__') and not
                                 callable(getattr(QuickChatSelection.QuickChatSelection, chat))],
                                list_name='quick_chat_list',
                                other_attributes=[
                                    ('CHAT_NONE', -1),
                                    ('CHAT_EVERYONE', False),
                                    ('CHAT_TEAM_ONLY', True)
],
    attribute_object=QuickChatSelection.QuickChatSelection)


def send_quick_chat_flat(game_interface, index, team, team_only, quick_chat):
    builder = flatbuffers.Builder(0)
    QuickChat.QuickChatStart(builder)
    QuickChat.QuickChatAddQuickChatSelection(builder, quick_chat)
    QuickChat.QuickChatAddPlayerIndex(builder, index)
    QuickChat.QuickChatAddTeamOnly(builder, team_only)
    result = QuickChat.QuickChatEnd(builder)

    builder.Finish(result)

    return game_interface.send_chat_flat(builder)


def send_quick_chat(queue_holder, index, team, team_only, quick_chat):
    """
    Sends a quick chat to the general queue for everyone to pull from
    :param queue_holder:
    :param index: The index of the player sending the message
    :param team: The team of the player sending the message
    :param team_only: if the message is team only
    :param quick_chat: The contents of the quick chat
    :return:
    """
    queue_holder["output"].put((index, team, team_only, quick_chat))
