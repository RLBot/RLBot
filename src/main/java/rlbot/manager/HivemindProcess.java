package rlbot.manager;

import java.util.HashSet;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicBoolean;

public class HivemindProcess {

    private final HashSet<Integer> droneIndexes = new HashSet<>();
    private AtomicBoolean runFlag;
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

    public void registerDrone(int index) {
        synchronized (this) {
            droneIndexes.add(index);
        }
    }

    public void retireDrone(int index) {
        synchronized (this) {
            droneIndexes.remove(index);
        }
    }

    public Set<Integer> getDroneIndexes() {
        synchronized (this) {
            return new HashSet<>(droneIndexes);
        }
    }
}
