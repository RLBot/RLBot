package rlbot;

import rlbot.flat.GameTickPacket;

import java.util.Map;
import java.util.Set;

public interface Hivemind {

    /**
     * <p>Hivemind logic goes here. Returns a mapping from drone indexes to ControllerStates based on the information
     * given in the GameTickPacket. Only return ControllerStates for the indexes included in the droneIndexes
     * argument.</p>
     *
     * <p>droneIndexes might change during the game if drones join or leave. Therefore you should make sure to check
     * whether the indexes you control are changed. For instance do:</p>
     * <pre>
     * {@code
     * if (oldIndexes.equals(droneIndexes)) {
     *     // Hive changed
     * }
     * oldIndexes = droneIndexes;
     * }
     * </pre>
     * where oldIndexes are a field in your hivemind.
     */
    Map<Integer, ControllerState> processInput(Set<Integer> droneIndexes, GameTickPacket request);

    /**
     * Shuts down the hive and close any resources it's using.
     */
    void retire();
}
