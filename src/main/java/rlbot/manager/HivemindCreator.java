package rlbot.manager;

import rlbot.Hivemind;

/**
 * This interface is used by the HivemindManager when multiple hiveminds per team are desired.
 */
public interface HivemindCreator {

    /**
     * Create a new hivemind instance.
     */
    Hivemind createHivemind(int team, String hiveKey);

    /**
     * Assign a hive key to the newly registered bot. This key will decide which hivemind the bot will
     * be controlled by.
     */
    String assignHiveKey(int index, int team, String botName);
}
