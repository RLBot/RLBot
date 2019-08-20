package rlbot.render;

import com.google.flatbuffers.FlatBufferBuilder;
import rlbot.cppinterop.RLBotDll;

/**
 * This renderer must be constructed with a specific unique name. You can draw, clear, etc. independently from
 * other renderers.
 */
public class NamedRenderer extends Renderer {
    public NamedRenderer(final String renderName) {
        super(renderName.hashCode());
    }

    public void startPacket() {
        builder = new FlatBufferBuilder(1000);
    }

    public RenderPacket finishPacket() {
        return doFinishPacket();
    }

    public void finishAndSend() {
        RLBotDll.sendRenderPacket(finishPacket());
    }
}
