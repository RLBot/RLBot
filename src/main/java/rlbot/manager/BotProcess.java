package rlbot.manager;

import java.util.concurrent.atomic.AtomicBoolean;

/**
 * Simple container for a thread that's intended to be running bot logic.
 */
public class BotProcess {
    private AtomicBoolean runFlag;
    private Thread thread;

    public BotProcess(Thread thread, final AtomicBoolean runFlag) {
        this.thread = thread;
        this.runFlag = runFlag;
    }

    public Thread getThread() {
        return thread;
    }

    public void stop() {
        runFlag.set(false);
    }
}
