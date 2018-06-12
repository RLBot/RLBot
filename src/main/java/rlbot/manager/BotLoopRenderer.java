package rlbot.manager;

import com.google.flatbuffers.FlatBufferBuilder;
import rlbot.Bot;
import rlbot.cppinterop.RLBotDll;
import rlbot.render.RenderPacket;
import rlbot.render.Renderer;

import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

public class BotLoopRenderer extends Renderer {

    private static Map<Integer, BotLoopRenderer> botLoopMap = new ConcurrentHashMap<>();
    private RenderPacket previousPacket = null;

    private BotLoopRenderer(int index) {
        super(index);
    }

    public static BotLoopRenderer forBotLoop(final Bot bot) {
        botLoopMap.computeIfAbsent(bot.getIndex(), BotLoopRenderer::new);
        return botLoopMap.get(bot.getIndex());
    }

    void startPacket() {
        builder = new FlatBufferBuilder(1000);
    }

    void finishAndSendIfDifferent() {
        RenderPacket packet = doFinishPacket();
        if (previousPacket == null || !previousPacket.equals(packet)) {
            RLBotDll.sendRenderPacket(packet);
            previousPacket = packet;
        }
    }
}
