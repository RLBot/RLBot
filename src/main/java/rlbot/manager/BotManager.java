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
        while (keepRunning && runFlag.get()) {
            try {
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
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }
        bot.retire();
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
        while (keepRunning) {

            try {
                latestPacket = RLBotDll.getFlatbufferPacket();
                synchronized (dinnerBell) {
                    dinnerBell.notifyAll();
                }
            } catch (IOException e) {
                e.printStackTrace();
            }

            try {
                // Fetch the latest game tick packet at 60 Hz.
                Thread.sleep(16);
            } catch (InterruptedException e) {
                throw new RuntimeException(e);
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
    }
}
