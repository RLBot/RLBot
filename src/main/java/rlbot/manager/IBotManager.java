package rlbot.manager;

import java.util.Set;

public interface IBotManager {

    void ensureStarted();

    /**
     * Returns a set of every bot index that is currently registered and running in this java process.
     * Will not include indices from humans, bots in other languages, or bots in other java processes.
     *
     * This may be useful for driving a basic status display.
     */
    Set<Integer> getRunningBotIndices();

    void shutDown();

    void retireBot(int index);

    /**
     * Sets the maximum amount of packets your bot will receive per second
     */
    void setRefreshRate(int refreshRate);

    void setSocketInfo(String socketHost, int socketPort);
}
