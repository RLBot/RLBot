import tempfile
import unittest
from pathlib import Path
import json
from contextlib import contextmanager

from rlbot.matchcomms.server import launch_matchcomms_server
from rlbot.matchcomms.client import MatchcommsClient
from rlbot.matchcomms.common_uses.reply import add_reply_field, reply_to
from rlbot.agents.base_agent import BaseAgent
from rlbot.matchcomms.common_uses.set_attributes_message import make_set_attributes_message, handle_set_attributes_message


@contextmanager
def connected_clients():
    server = launch_matchcomms_server()
    client1 = MatchcommsClient(server.root_url)
    client2 = MatchcommsClient(server.root_url)
    yield client1, client2
    client2.close()
    client1.close()
    server.close()


class TrainingTest(unittest.TestCase):

    def test_reply_round_trip(self):
        with connected_clients() as (client1, client2):
            msg0 = {'ho': 1}
            reply_id = add_reply_field(msg0)
            client2.outgoing_broadcast.put_nowait(msg0)
            msg1 = client1.incoming_broadcast.get(timeout=.1)
            self.assertEqual(msg1.get('ho', None), 1)
            reply_to(client1, msg1, {'hi': 'there'})
            msg2 = client2.incoming_broadcast.get(timeout=.1)
            self.assertEqual(msg2.get('hi', None), 'there')
            self.assertEqual(msg2.get('ho', None), None)

    def test_set_attributes_message(self):
        class FakeAgent(BaseAgent):
            pass
        agent = FakeAgent(name='bob', team=1, index=2)
        agent.attr1 = 41
        agent.attr2 = 50

        self.assertTrue(
            handle_set_attributes_message(
                make_set_attributes_message(2, {'attr1': 42}),
                agent,
            )
        )
        self.assertEqual(agent.attr1, 42)
        self.assertEqual(agent.attr2, 50)

        self.assertFalse(
            handle_set_attributes_message(
                make_set_attributes_message(0, {'attr1': 43}),
                agent,
            )
        )
        self.assertEqual(agent.attr1, 42)
        self.assertEqual(agent.attr2, 50)

        self.assertTrue(
            handle_set_attributes_message(
                make_set_attributes_message(2, {'attr1': 70, 'attr2': 60}),
                agent,
                allowed_keys=['attr2'],
            )
        )
        self.assertEqual(agent.attr1, 42)
        self.assertEqual(agent.attr2, 60)


if __name__ == '__main__':
    unittest.main()
