package rlbot.manager;

import rlbot.Bot;
import rlbot.ControllerState;
import rlbot.cppinterop.RLBotDll;
import rlbot.cppinterop.RLBotInterfaceException;
import rlbot.flat.GameTickPacket;
import rlbot.pyinterop.BaseSocketServer;

import java.io.IOException;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.function.Supplier;

/**
 * This class is a BotManager for single bots.
 */
public class BotManager extends BaseBotManager {

    protected final Map<Integer, BotProcess> botProcesses = new ConcurrentHashMap<>();

    public void ensureBotRegistered(final int index, final int team, final Supplier<Bot> botSupplier) {
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

    /**
     * Returns a set of every bot index that is currently registered and running in this java process.
     * Will not include indices from humans, bots in other languages, or bots in other java processes.
     *
     * This may be useful for driving a basic status display.
     */
    @Override
    public Set<Integer> getRunningBotIndices() {
        return botProcesses.keySet();
    }

    @Override
    public void shutDown() {
        super.shutDown();
        botProcesses.clear();
    }

    @Override
    public void retireBot(int index) {
        BotProcess process = botProcesses.get(index);
        if (process != null) {
            process.stop();
            botProcesses.remove(index);
        }
        RLBotDll.setPlayerInputFlatbuffer(new EmptyControls(), index);
    }
}
