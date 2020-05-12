package rlbot.manager;

import java.util.HashSet;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicBoolean;

public class HivemindProcess {

    public AtomicBoolean runFlag;

    private final HashSet<Integer> droneIndices = new HashSet<>();
    private Thread thread;

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

    public void ensureStarted() {
        runFlag.set(true);
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
