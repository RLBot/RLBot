import tempfile
import unittest
from pathlib import Path
import json

from rlbot.matchconfig.loadout_config import LoadoutConfig, LoadoutPaintConfig
from rlbot.matchconfig.match_config import MatchConfig
from rlbot.matchconfig.conversions import read_match_config_from_file, ConfigJsonEncoder, as_match_config

class TrainingTest(unittest.TestCase):

    def test_parse_round_trip(self):
        rlbot_cfg = Path(__file__).absolute().parent.parent.parent.parent.parent / 'rlbot.cfg'
        match_config_1 = read_match_config_from_file(rlbot_cfg)
        with tempfile.TemporaryDirectory() as tmpdirname:
            tmp_path = Path(tmpdirname)
            json_1_path = tmp_path / 'json_1.json'
            json_2_path = tmp_path / 'json_2.json'
            with open(json_1_path, 'w') as f:
                json.dump(match_config_1, f, cls=ConfigJsonEncoder, sort_keys=True)
            with open(json_1_path) as f:
                match_config_2 = json.load(f, object_hook=as_match_config)
            self.assertEqual(match_config_1, match_config_2)

            with open(json_1_path) as f:
                json_1 = f.read()
            with open(json_2_path, 'w') as f:
                json.dump(match_config_2, f, cls=ConfigJsonEncoder, sort_keys=True)
            with open(json_2_path) as f:
                json_2 = f.read()
            self.assertEqual(json_1, json_2)

if __name__ == '__main__':
    unittest.main()
