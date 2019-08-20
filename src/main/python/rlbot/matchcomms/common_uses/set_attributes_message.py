from typing import List, Optional

from rlbot.matchcomms.common_uses.common_keys import TARGET_PLAYER_INDEX
from rlbot.matchcomms.shared import JSON
from rlbot.agents.base_agent import BaseAgent

"""
This message instructs a certain player to persist some attribute.
"""

MESSAGE_KEY = 'setattrs'
ALL_KEYS_ALLOWED = None


def make_set_attributes_message(target_player_index: int, attrs: JSON) -> JSON:
    assert type(attrs) is dict
    return {
        TARGET_PLAYER_INDEX: target_player_index,
        MESSAGE_KEY: attrs,
    }

def handle_set_attributes_message(msg: JSON, player: BaseAgent, allowed_keys: Optional[List[str]]=ALL_KEYS_ALLOWED) -> bool:
    """
    Sets attributes on the player if the message was applicable for this task.
    If allowed_keys is specified, any key not in this list is silently dropped.
    Returns True iff the message was fully handled by this function.
    """
    attrs = msg.get(MESSAGE_KEY, None)
    if type(attrs) != dict: return False
    if msg.get(TARGET_PLAYER_INDEX, None) != player.index: return False

    # Copy values from attrs to the player.
    if allowed_keys is ALL_KEYS_ALLOWED:
        for k,v in attrs.items():
            setattr(player, k, v)
    else:
        for k in allowed_keys:
            if k in attrs:
                setattr(player, k, attrs[k])
    return True
