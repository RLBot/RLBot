import time
from collections import namedtuple, defaultdict
from typing import Optional, List
import random
import string
from queue import Empty

from rlbot.matchcomms.client import MatchcommsClient
from rlbot.matchcomms.shared import JSON

MESSAGE_KEY = 'reply_id'

ReplyId = str  # type alias
ID_CHARACTER_OPTIONS = string.ascii_uppercase + string.ascii_lowercase + string.digits


def add_reply_field(outgoing_msg: JSON) -> ReplyId:
    """
    Mutates outgoing_msg to gain a reply_id and returns the reply_id.
    """
    assert not hasattr(outgoing_msg, MESSAGE_KEY), "Message contents conflict with reply MESSAGE_KEY."
    reply_id = generate_random_reply_id()
    outgoing_msg[MESSAGE_KEY] = reply_id
    return reply_id


def reply_to(matchcomms: MatchcommsClient, incoming_msg: JSON, outgoing_msg: JSON = None):
    """
    Mutates outgoing_msg (empty message by default) to gain the reply_id of
    the incoming_msg and broadcasts it.
    """
    if outgoing_msg is None:
        outgoing_msg = {}
    assert not hasattr(outgoing_msg, MESSAGE_KEY), "Message contents conflict with reply MESSAGE_KEY."
    outgoing_msg[MESSAGE_KEY] = get_reply_id(incoming_msg)
    matchcomms.outgoing_broadcast.put_nowait(outgoing_msg)

def is_reply_msg(msg: JSON) -> bool:
    return bool(get_reply_id(msg))


def get_reply_id(msg: JSON) -> Optional[ReplyId]:
    if type(msg) != dict: return None
    return msg.get(MESSAGE_KEY, None)

def generate_random_reply_id():
    return ''.join(random.choice(ID_CHARACTER_OPTIONS) for _ in range(10))



class ResponseDeadlineExceeded(Exception):
    pass

RecievedMessages = namedtuple('RecievedMessages', 'replies unhandled_messages')
def send_and_wait_for_replies(
        matchcomms: MatchcommsClient, outgoing_msgs: List[JSON],
        timeout_seconds=0.1, num_retries=2) -> RecievedMessages:
    """
    Sends all outgoing_msgs then blocks until all of them got a reply.
    Raises a ResponseDeadlineExceeded exception if the number of reties htimeout is reached.
    """
    unhandled_messages = []
    reply_ids = set(add_reply_field(msg) for msg in outgoing_msgs)
    replies = defaultdict(list) # ReplyId -> List[JSON]
    for i in range(num_retries + 1):
        # (re)-send messages that have not gotten a reply yet
        for msg in outgoing_msgs:
            if get_reply_id(msg) not in replies:
                matchcomms.outgoing_broadcast.put_nowait(msg)

        # Poll for replies until the timeout.
        begin = time.time()
        while time.time() - begin < timeout_seconds:
            try:
                msg = matchcomms.incoming_broadcast.get_nowait()
            except Empty:
                time.sleep(0.002)
                continue
            reply_id = get_reply_id(msg)
            if reply_id not in reply_ids:
                unhandled_messages.append(msg)
                continue
            replies[reply_id].append(msg)
            if len(replies) == len(outgoing_msgs):
                return RecievedMessages(replies=replies, unhandled_messages=unhandled_messages)

    unreplied_messages = [msg for msg in outgoing_msgs if get_reply_id(msg) not in replies]
    raise ResponseDeadlineExceeded(f'Did not get responses to these messages: {unreplied_messages}')

