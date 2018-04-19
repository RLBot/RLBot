package rlbot.manager;

import rlbot.Bot;

import java.util.concurrent.atomic.AtomicBoolean;

public class BotProcess {
    private Bot bot;
    private AtomicBoolean runFlag;
    private Thread thread;

    public BotProcess(Bot bot, Thread thread, final AtomicBoolean runFlag) {
        this.bot = bot;
        this.thread = thread;
        this.runFlag = runFlag;
    }

    public Bot getBot() {
        return bot;
    }

    public Thread getThread() {
        return thread;
    }

    public void stop() {
        runFlag.set(false);
    }
}
