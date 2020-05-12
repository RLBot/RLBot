package rlbot;

import rlbot.flat.GameTickPacket;

import java.util.Map;
import java.util.Set;

public interface Hivemind {

    /**
     * <p>Hivemind logic goes here. Returns a mapping from drone indices to ControllerStates based on the information
     * given in the GameTickPacket. Only return ControllerStates for the indices included in the droneIndices
     * argument.</p>
     *
     * <p>droneIndices might change during the game if drones join or leave. Therefore you should make sure to check
     * whether the indices you control are changed. For instance do:</p>
     * <pre>
     * {@code
     * if (oldIndices.equals(droneIndices)) {
     *     // Hive changed
     * }
     * oldIndices = droneIndices;
     * }
     * </pre>
     * where oldIndices are a field in your hivemind.
     */
    Map<Integer, ControllerState> processInput(Set<Integer> droneIndices, GameTickPacket request);

    /**
     * Shuts down the hive and close any resources it's using.
     */
    void retire();
}
