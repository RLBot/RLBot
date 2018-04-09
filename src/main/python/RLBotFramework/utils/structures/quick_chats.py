import multiprocessing
import queue
from threading import Thread
from multiprocessing import Manager

import time

from RLBotFramework.utils.logging_utils import get_logger


def get_quick_chats():
    quick_chat_list = ["Information_IGotIt",
                       "Information_NeedBoost",
                       "Information_TakeTheShot",
                       "Information_Defending",
                       "Information_GoForIt",
                       "Information_Centering",
                       "Information_AllYours",
                       "Information_InPosition",
                       "Information_Incoming",
                       "Compliments_NiceShot",
                       "Compliments_GreatPass",
                       "Compliments_Thanks",
                       "Compliments_WhatASave",
                       "Compliments_NiceOne",
                       "Compliments_WhatAPlay",
                       "Compliments_GreatClear",
                       "Compliments_NiceBlock",
                       "Reactions_OMG",
                       "Reactions_Noooo",
                       "Reactions_Wow",
                       "Reactions_CloseOne",
                       "Reactions_NoWay",
                       "Reactions_HolyCow",
                       "Reactions_Whew",
                       "Reactions_Siiiick",
                       "Reactions_Calculated",
                       "Reactions_Savage",
                       "Reactions_Okay",
                       "Apologies_Cursing",
                       "Apologies_NoProblem",
                       "Apologies_Whoops",
                       "Apologies_Sorry",
                       "Apologies_MyBad",
                       "Apologies_Oops",
                       "Apologies_MyFault",
                       "PostGame_Gg",
                       "PostGame_WellPlayed",
                       "PostGame_ThatWasFun",
                       "PostGame_Rematch",
                       "PostGame_OneMoreGame",
                       "PostGame_WhatAGame",
                       "PostGame_NiceMoves",
                       "PostGame_EverybodyDance"]
    result = lambda: None
    for i in range(len(quick_chat_list)):
        setattr(result, quick_chat_list[i], i)
    setattr(result, 'quick_chat_list', quick_chat_list)
    setattr(result, 'CHAT_NONE', -1)
    setattr(result, 'CHAT_EVERYONE', False)
    setattr(result, 'CHAT_TEAM_ONLY', True)
    return result


QuickChats = get_quick_chats()


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
