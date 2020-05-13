package rlbot.manager;

import java.util.HashSet;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicBoolean;

/**
 * This class contains information about a hivemind process and the indices that the hivemind controls.
 */
public class HivemindProcess {

    private final AtomicBoolean runFlag;

    private final HashSet<Integer> droneIndices = new HashSet<>();
    private final Thread thread;

    public HivemindProcess(Thread thread, final AtomicBoolean runFlag) {
        this.thread = thread;
        this.runFlag = runFlag;
    }

    public Thread getThread() {
        return thread;
    }

    public void stop() {
        runFlag.set(false);
    }

    public boolean isRunning() {
        return runFlag.get();
    }

    public void registerDrone(int index) {
        synchronized (this) {
            droneIndices.add(index);
        }
    }

    public void retireDrone(int index) {
        synchronized (this) {
            droneIndices.remove(index);
        }
    }

    public Set<Integer> getDroneIndices() {
        synchronized (this) {
            return new HashSet<>(droneIndices);
        }
    }
}
