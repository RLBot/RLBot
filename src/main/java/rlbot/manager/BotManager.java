package rlbot.manager;

import com.google.protobuf.InvalidProtocolBufferException;
import rlbot.Bot;
import rlbot.api.GameData;
import rlbot.cpp.RLBotDll;

import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.function.Supplier;

public class BotManager {

    private final Map<Integer, BotProcess> botProcesses = new HashMap<>();

    private boolean keepRunning;

    private final Object dinnerBell = new Object();
    private  GameData.GameTickPacket latestPacket;

    public void ensureBotRegistered(final int index, final Supplier<Bot> botSupplier) {
        if (botProcesses.containsKey(index)) {
            return;
        }

        final Bot bot = botSupplier.get();

        botProcesses.computeIfAbsent(index, (idx) -> {
            final AtomicBoolean runFlag = new AtomicBoolean(true);
            Thread botThread = new Thread(() -> doRunBot(bot, index, runFlag));
            botThread.start();
            return new BotProcess(bot, botThread, runFlag);
        });
    }

    private void doRunBot(final Bot bot, final int index, final AtomicBoolean runFlag) {
        while (keepRunning && runFlag.get()) {
            try {
                synchronized (dinnerBell) {
                    dinnerBell.wait(1000);
                }
                GameData.ControllerState controllerState = bot.processInput(latestPacket);
                RLBotDll.setControllerState(controllerState, index);
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

    private void doLoop() {
        while (keepRunning) {

            try {
                latestPacket = RLBotDll.getProtoPacket();
                synchronized (dinnerBell) {
                    dinnerBell.notifyAll();
                }

            } catch (InvalidProtocolBufferException e) {
                e.printStackTrace();
            }

            try {
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
