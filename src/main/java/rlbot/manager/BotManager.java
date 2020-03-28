package rlbot.manager;

import rlbot.Bot;
import rlbot.ControllerState;
import rlbot.cppinterop.RLBotDll;
import rlbot.cppinterop.RLBotInterfaceException;
import rlbot.flat.GameTickPacket;

import java.io.IOException;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.function.Supplier;

/**
 * This class keeps track of all the bots, runs the main logic loops, and retrieves the
 * game data on behalf of the bots.
 */
public class BotManager {

    private final Map<Integer, BotProcess> botProcesses = new ConcurrentHashMap<>();

    private boolean keepRunning;

    private final Object dinnerBell = new Object();
    private GameTickPacket latestPacket;
    private AtomicInteger refreshRate = new AtomicInteger(60);

    public void ensureBotRegistered(final int index, final Supplier<Bot> botSupplier) {
        if (botProcesses.containsKey(index)) {
            return;
        }

        botProcesses.computeIfAbsent(index, (idx) -> {
            final Bot bot = botSupplier.get();
            final AtomicBoolean runFlag = new AtomicBoolean(true);
            Thread botThread = new Thread(() -> doRunBot(bot, index, runFlag));
            botThread.start();
            return new BotProcess(botThread, runFlag);
        });
    }

    private void doRunBot(final Bot bot, final int index, final AtomicBoolean runFlag) {

        final BotLoopRenderer renderer = BotLoopRenderer.forBotLoop(bot);
        try {
            while (keepRunning && runFlag.get()) {

                synchronized (dinnerBell) {
                    // Wait for the main thread to indicate that we have new game tick data.
                    dinnerBell.wait(1000);
                }
                if (latestPacket != null) {
                    renderer.startPacket();
                    ControllerState controllerState = bot.processInput(latestPacket);
                    RLBotDll.setPlayerInputFlatbuffer(controllerState, index);
                    renderer.finishAndSendIfDifferent();
                }
            }
        } catch (Exception e) {
            System.out.println("Bot died because an exception occurred in the run loop!");
            e.printStackTrace();
        } finally {
            retireBot(index); // Unregister this bot internally.
            bot.retire(); // Tell the bot to clean up its resources.
        }
    }

    public void ensureStarted() {
        if (keepRunning) {
            return; // Already started
        }

        keepRunning = true;
        Thread looper = new Thread(this::doLoop);
        looper.start();
    }

    /**
     * Returns a set of every bot index that is currently registered and running in this java process.
     * Will not include indices from humans, bots in other languages, or bots in other java processes.
     *
     * This may be useful for driving a basic status display.
     */
    public Set<Integer> getRunningBotIndices() {
        return botProcesses.keySet();
    }

    private void doLoop() {
        // Minimum call rate when paused.
        final long MAX_AGENT_CALL_PERIOD = 1000 / 30;

        long lastCallRealTime = System.currentTimeMillis();
        float lastTickGameTime = 0;
        boolean usingLockstep = false;

        try {
            usingLockstep = RLBotDll.getMatchSettings().enableLockstep();
        } catch (final RLBotInterfaceException e) {
            e.printStackTrace();
        }

        try {
            latestPacket = RLBotDll.getFlatbufferPacket();
            lastTickGameTime = latestPacket.gameInfo().secondsElapsed();
        } catch (RLBotInterfaceException e) {
            e.printStackTrace();
        }

        // Set the initial value so that as urgency flips up and down, the variation will be centered over
        // the threshold (0 urgency) and have minimal likelihood of drifting away and skipping a frame
        float frameUrgency = -0.5f / this.refreshRate.get();

        while (keepRunning) {
            // Python version: https://github.com/RLBot/RLBot/blob/master/src/main/python/rlbot/botmanager/bot_manager.py#L194-L212
            final int refreshRate = this.refreshRate.get();
            try {
                // Retrieve latest packet
                if (usingLockstep) {
                    latestPacket = RLBotDll.getCurrentFlatbufferPacket();
                } else {
                    latestPacket = RLBotDll.getFlatbufferPacket();
                }

                // Run the bot only if gameInfo has updated
                final float tickGameTime = latestPacket.gameInfo().secondsElapsed();
                final long now = System.currentTimeMillis();
                final boolean shouldCallWhilePaused = now - lastCallRealTime >= MAX_AGENT_CALL_PERIOD;

                // Urgency increases every frame, but don't let it build up a large backlog
                frameUrgency += tickGameTime - lastTickGameTime;
                frameUrgency = clamp(frameUrgency, -1f / refreshRate, 1f / refreshRate);

                if((tickGameTime != lastTickGameTime || shouldCallWhilePaused) && frameUrgency >= 0 || usingLockstep){
                    lastCallRealTime = now;
                    // Urgency decreases when a tick is processed.
                    frameUrgency -= 1f / refreshRate;
                    synchronized (dinnerBell) {
                        dinnerBell.notifyAll();
                    }
                }

                lastTickGameTime = tickGameTime;

                if (usingLockstep) {
                    try {
                        Thread.sleep(1000 / refreshRate);
                    } catch (InterruptedException e) {
                        throw new RuntimeException(e);
                    }
                }
            } catch (IOException e) {
                e.printStackTrace();
            }
        }
    }

    public void shutDown() {
        keepRunning = false;
        botProcesses.clear();
    }

    public void retireBot(int index) {
        BotProcess process = botProcesses.get(index);
        if (process != null) {
            process.stop();
            botProcesses.remove(index);
        }
        RLBotDll.setPlayerInputFlatbuffer(new EmptyControls(), index);
    }

    /**
     * Sets the maximum amount of packets your bot will receive per second
     */
    public void setRefreshRate(int refreshRate){
        // Cap the refresh between 30hz and 120hz
        this.refreshRate.set(clamp(refreshRate, 30, 120));
    }

    private static int clamp(int value, int min, int max) {
        return Math.max(min, Math.min(value, max));
    }

    private static float clamp(float value, float min, float max) {
        return Math.max(min, Math.min(value, max));
    }
}
