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
                                 if not chat.startswith('__')
                                 and not callable(getattr(QuickChatSelection.QuickChatSelection, chat))],
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


def register_for_quick_chat(queue_holder, called_func, quit_event):
    """
    Registers a function to be called anytime this queue gets a quick chat.
    :param queue_holder:  This holds the queues for the bots
    :param called_func: This is the function that is called when a quick chat is received
    :param quit_event: This event will be set when rlbot is trying to shut down
    :return: The newly created thread.
    """

    def threaded_func(chat_queue, called_func, quit_event):
        while not quit_event.is_set():
            try:
                next_message = chat_queue.get(timeout=0.01)
                index, team, chat = next_message
                called_func(index, team, chat)
            except queue.Empty:
                pass
        return

    thread = Thread(target=threaded_func, args=(queue_holder["input"], called_func, quit_event))
    thread.start()
    return thread


class QuickChatManager:
    bot_queues = {}

    def __init__(self, game_interface):
        self.game_interface = game_interface
        self.manager = multiprocessing.Manager()
        self.general_chat_queue = self.manager.Queue()
        self.logger = get_logger('chats')

    def create_queue_for_bot(self, index, team):
        bot_queue = self.manager.Queue()
        queue_holder = dict()
        queue_holder["input"] = bot_queue
        queue_holder["output"] = self.general_chat_queue
        self.bot_queues[index] = (team, bot_queue)
        return queue_holder

    def process_queue(self, quit_event):
        while not quit_event.is_set():

            try:
                next_message = self.general_chat_queue.get(timeout=0.01)
                index, team, team_only, message_details = next_message
                self.logger.debug('got quick chat from bot %s on team %s with message %s:', index, team,
                                  QuickChats.quick_chat_list[message_details])
                for i in self.bot_queues:
                    bots = self.bot_queues[i]
                    if i == index:
                        # do not send yourself a message
                        continue
                    if bots[0] != team and team_only:
                        # do not send to other team if team only
                        continue
                    bots[1].put((index, team, message_details))
                self.game_interface.send_chat(index, team_only, message_details)
            except queue.Empty:
                pass

    def start_manager(self, quit_event):
        thread = Thread(target=self.process_queue, args=(quit_event,))
        thread.start()
        return thread
