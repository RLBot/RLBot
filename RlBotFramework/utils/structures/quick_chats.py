import multiprocessing
from threading import Thread
from multiprocessing import Manager

import time


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


def register_for_quick_chat(queue_holder, is_game_running, called_func):
    """
    Registers a function to be called anytime this queue gets a quick chat.
    :param queue_holder:  This holds the queues for the bots
    :param is_game_running: This returns true while the game is running.
                            Should return false once the game is no longer running.
    :param called_func: This is the function that is called when a quick chat is received
    :return: The newly created thread.
    """

    def threaded_func(queue, is_game_running, called_func):
        while is_game_running():
            next_message = queue.get()
            if next_message is None:
                time.sleep(0.01)  # sleep for 1/100th of a second
                continue
            called_func(next_message)
        return
    thread = Thread(target=threaded_func, args=(queue_holder["input"], is_game_running, called_func))
    thread.start()
    return thread


class QuickChatManager:
    bot_queues = {}
    game_running = True

    def __init__(self, game_interface):
        self.game_interface = game_interface
        self.general_chat_queue = multiprocessing.Queue()

    def create_queue_for_bot(self, index, team):
        bot_queue = multiprocessing.Queue()
        with Manager() as manager:
            queue_holder = manager.dict()
            queue_holder["input"] = bot_queue
            queue_holder["output"] = self.general_chat_queue
            self.bot_queues[index] = (team, bot_queue)
            return queue_holder

    def process_queue(self):
        while self.game_running:
            next_message = self.general_chat_queue.get()
            if next_message is None:
                time.sleep(0.01)  # sleep for 1/100th of a second
                continue
            index, team, team_only, message_details = next_message
            for i in self.bot_queues:
                bots = self.bot_queues[i]
                if i == index:
                    # do not send yourself a message
                    continue
                if bots[0] != team and team_only:
                    # do not send to other team if team only
                    continue
                bots[1].put((index, message_details))
