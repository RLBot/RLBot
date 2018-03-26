package rlbot.manager;

import rlbot.Bot;

public class BotProcess {
    private Bot bot;
    private Thread thread;

    public BotProcess(Bot bot, Thread thread) {
        this.bot = bot;
        this.thread = thread;
    }

    public Bot getBot() {
        return bot;
    }

    public Thread getThread() {
        return thread;
    }
}
