package rlbot.manager;

import rlbot.Bot;
import rlbot.ControllerState;
import rlbot.cppinterop.RLBotDll;
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

        long rateLimitTime = System.currentTimeMillis();

        float lastTickGameTime = -1;
        float frameUrgency = 0;
        long lastCallRealTime = System.currentTimeMillis();
        while (keepRunning) {
            // Python version: https://github.com/RLBot/RLBot/blob/master/src/main/python/rlbot/botmanager/bot_manager.py#L194-L212
            final int refreshRate = this.refreshRate.get();
            try{
                // Retrieve latest packet
                latestPacket = RLBotDll.getFlatbufferPacket();

                // Run the bot only if gameInfo has updated
                final float tickGameTime = latestPacket.gameInfo().secondsElapsed();
                final long now = System.currentTimeMillis();
                final boolean shouldCallWhilePaused = now - lastCallRealTime >= MAX_AGENT_CALL_PERIOD;

                if(lastTickGameTime < 0 || lastTickGameTime > tickGameTime + 1) // Make sure we don't mess up our frameUrgency when the bot starts in the middle of the game
                    lastTickGameTime = tickGameTime - (1f / refreshRate);

                if(frameUrgency < 4f / refreshRate) // Urgency increases every frame, but don't let it build up a large backlog
                    frameUrgency += tickGameTime - lastTickGameTime;

                if((tickGameTime != lastTickGameTime || shouldCallWhilePaused) && frameUrgency >= 0){
                    lastCallRealTime = now;
                    // Urgency decreases when a tick is processed.
                    frameUrgency -= 1f / refreshRate;
                    synchronized (dinnerBell) {
                        dinnerBell.notifyAll();
                    }
                }

                lastTickGameTime = tickGameTime;

                try{
                    long timeout = 1000 / (2 * refreshRate); // https://en.wikipedia.org/wiki/Nyquist_rate
                    // Subtract the target time by the current time
                    timeout = (rateLimitTime + timeout) - System.currentTimeMillis();
                    // Make sure that no errors are thrown
                    timeout = Math.max(0, timeout);
                    Thread.sleep(timeout);
                }catch (InterruptedException e){
                    throw new RuntimeException(e);
                }

            }catch (IOException e){
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
        this.refreshRate.set(Math.max(30, Math.min(120, refreshRate)));
    }
}
