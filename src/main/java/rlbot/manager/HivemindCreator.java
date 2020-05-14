package rlbot.manager;

import rlbot.Hivemind;

public interface HivemindCreator {

    Hivemind createHivemind(int team, String hiveKey);

    String assignHiveKey(int index, int team, String botName);
}
