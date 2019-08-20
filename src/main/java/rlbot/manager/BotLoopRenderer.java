package rlbot.manager;

import com.google.flatbuffers.FlatBufferBuilder;
import rlbot.Bot;
import rlbot.cppinterop.RLBotDll;
import rlbot.render.RenderPacket;
import rlbot.render.Renderer;

import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

/**
 * A renderer that will be managed automatically. Users of this renderer should expect the packet
 * to be started and finished on a regular basis without their intervention.
 */
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
        if (!packet.equals(previousPacket)) {
            RLBotDll.sendRenderPacket(packet);
            previousPacket = packet;
        }
    }
}
