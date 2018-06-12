package rlbot.render;

import com.google.flatbuffers.FlatBufferBuilder;
import rlbot.cppinterop.RLBotDll;
import rlbot.flat.*;
import rlbot.flat.Color;

import java.awt.*;
import java.util.*;
import java.util.List;

public abstract class Renderer {

    private final int index;

    private List<Integer> renderMessageOffsets = new LinkedList<>();
    protected FlatBufferBuilder builder;

    protected Renderer(int index) {
        this.index = index;
    }

    protected RenderPacket doFinishPacket() {

        int[] offsets = renderMessageOffsets.stream().mapToInt(i->i).toArray();
        int messagesOffset = RenderGroup.createRenderMessagesVector(builder, offsets);
        int renderGroupOffset = RenderGroup.createRenderGroup(builder, messagesOffset, index);

        builder.finish(renderGroupOffset);
        byte[] bytes = builder.sizedByteArray();

        resetPacket();
        return new RenderPacket(bytes);
    }

    /**
     * Removes any draw calls that have been queued up and starts over.
     * Can be called at any time.
     */
    public void resetPacket() {
        builder = null;
        renderMessageOffsets.clear();
    }

    /**
     * If this renderer has previously drawn anything on the screen, it will be erased.
     * This can be called at any time. It will not interrupt any packet construction
     * that may be in progress.
     */
    public void eraseFromScreen() {
        FlatBufferBuilder eraseBuilder = new FlatBufferBuilder(10);
        int messagesOffset = RenderGroup.createRenderMessagesVector(eraseBuilder, new int[0]);
        RenderGroup.startRenderGroup(eraseBuilder);
        RenderGroup.addRenderMessages(eraseBuilder, messagesOffset);
        RenderGroup.addId(eraseBuilder, index);
        eraseBuilder.finish(RenderGroup.endRenderGroup(eraseBuilder));

        RenderPacket emptyPacket = new RenderPacket(eraseBuilder.sizedByteArray());
        RLBotDll.sendRenderPacket(emptyPacket);
    }

    /**
     * Returns true if any draw calls have been queued up for the current packet.
     */
    public boolean hasContent() {
        return builder != null && builder.offset() > 0;
    }

    /**
     * Draws a line in screen coordinates.
     */
    public void drawLine2d(java.awt.Color color, Point start, Point end) {

        int colorOffset = Color.createColor(builder, color.getAlpha(), color.getRed(), color.getGreen(), color.getBlue());

        RenderMessage.startRenderMessage(builder);
        RenderMessage.addRenderType(builder, RenderType.DrawLine2D);
        RenderMessage.addColor(builder, colorOffset);
        RenderMessage.addStart(builder, Vector3.createVector3(builder, start.x, start.y, 0));
        RenderMessage.addEnd(builder, Vector3.createVector3(builder, end.x, end.y, 0));
        int finalOffset = RenderMessage.endRenderMessage(builder);

        renderMessageOffsets.add(finalOffset);
    }

    /**
     * Draws a line between two 3D coordinates.
     */
    public void drawLine3d(java.awt.Color color, rlbot.vector.Vector3 start, rlbot.vector.Vector3 end) {

        int colorOffset = Color.createColor(builder, color.getAlpha(), color.getRed(), color.getGreen(), color.getBlue());

        RenderMessage.startRenderMessage(builder);
        RenderMessage.addRenderType(builder, RenderType.DrawLine3D);
        RenderMessage.addColor(builder, colorOffset);
        RenderMessage.addStart(builder, start.toFlatbuffer(builder));
        RenderMessage.addEnd(builder, end.toFlatbuffer(builder));
        int finalOffset = RenderMessage.endRenderMessage(builder);

        renderMessageOffsets.add(finalOffset);
    }

    /**
     * Draws a 2D line which starts at screen coordinates and ends at a 3D coordinate.
     */
    public void drawLine2d3d(java.awt.Color color, Point start, rlbot.vector.Vector3 end) {

        int colorOffset = Color.createColor(builder, color.getAlpha(), color.getRed(), color.getGreen(), color.getBlue());

        RenderMessage.startRenderMessage(builder);
        RenderMessage.addRenderType(builder, RenderType.DrawLine2D_3D);
        RenderMessage.addColor(builder, colorOffset);
        RenderMessage.addStart(builder, Vector3.createVector3(builder, start.x, start.y, 0));
        RenderMessage.addEnd(builder, end.toFlatbuffer(builder));
        int finalOffset = RenderMessage.endRenderMessage(builder);

        renderMessageOffsets.add(finalOffset);
    }

    /**
     * This draws a 2D rectangle in screen coordinates.
     * @param upperLeft The upper left corner of the rectangle.
     * @param width in pixels.
     * @param height in pixels.
     * @param filled true if the rectangle should be filled in.
     */
    public void drawRectangle2d(java.awt.Color color, Point upperLeft, int width, int height, boolean filled) {

        int colorOffset = Color.createColor(builder, color.getAlpha(), color.getRed(), color.getGreen(), color.getBlue());

        RenderMessage.startRenderMessage(builder);
        RenderMessage.addRenderType(builder, RenderType.DrawRect2D);
        RenderMessage.addColor(builder, colorOffset);
        RenderMessage.addStart(builder, Vector3.createVector3(builder, upperLeft.x, upperLeft.y, 0));
        RenderMessage.addScaleX(builder, width);
        RenderMessage.addScaleY(builder, height);
        RenderMessage.addIsFilled(builder, filled);
        int finalOffset = RenderMessage.endRenderMessage(builder);

        renderMessageOffsets.add(finalOffset);
    }

    /**
     * This draws a 2D rectangle at a 3D-tracked position.
     * @param upperLeft The upper left corner of the rectangle.
     * @param width in pixels.
     * @param height in pixels.
     * @param filled true if the rectangle should be filled in.
     */
    public void drawRectangle3d(java.awt.Color color, rlbot.vector.Vector3 upperLeft, int width, int height, boolean filled) {
        drawRect3d(color, upperLeft, width, height, filled, false);
    }

    /**
     * This draws a 2D rectangle at a 3D-tracked position.
     * @param position The center of the rectangle.
     * @param width in pixels.
     * @param height in pixels.
     * @param filled true if the rectangle should be filled in.
     */
    public void drawCenteredRectangle3d(java.awt.Color color, rlbot.vector.Vector3 position, int width, int height, boolean filled) {
        drawRect3d(color, position, width, height, filled, true);
    }

    private void drawRect3d(java.awt.Color color, rlbot.vector.Vector3 position, int width, int height, boolean filled, boolean centered) {

        int colorOffset = Color.createColor(builder, color.getAlpha(), color.getRed(), color.getGreen(), color.getBlue());

        RenderMessage.startRenderMessage(builder);
        RenderMessage.addRenderType(builder, centered ? RenderType.DrawCenteredRect3D : RenderType.DrawRect3D);
        RenderMessage.addColor(builder, colorOffset);
        RenderMessage.addStart(builder, position.toFlatbuffer(builder));
        RenderMessage.addScaleX(builder, width);
        RenderMessage.addScaleY(builder, height);
        RenderMessage.addIsFilled(builder, filled);
        int finalOffset = RenderMessage.endRenderMessage(builder);

        renderMessageOffsets.add(finalOffset);
    }

    /**
     * Draws a string in screen coordinates.
     * @param upperLeft the location of the upper left corner of the text.
     * @param scaleX multiplier for the width of the text.
     * @param scaleY multiplier for the height of the text.
     */
    public void drawString2d(String text, java.awt.Color color, Point upperLeft, int scaleX, int scaleY) {

        int colorOffset = Color.createColor(builder, color.getAlpha(), color.getRed(), color.getGreen(), color.getBlue());
        int textOffset = builder.createString(text);

        RenderMessage.startRenderMessage(builder);
        RenderMessage.addRenderType(builder, RenderType.DrawString2D);
        RenderMessage.addColor(builder, colorOffset);
        RenderMessage.addStart(builder, Vector3.createVector3(builder, upperLeft.x, upperLeft.y, 0));
        RenderMessage.addScaleX(builder, scaleX);
        RenderMessage.addScaleY(builder, scaleY);
        RenderMessage.addText(builder, textOffset);
        int finalOffset = RenderMessage.endRenderMessage(builder);

        renderMessageOffsets.add(finalOffset);
    }

    /**
     * Draws a string in 2D, but the upper-left corner is at a 3D-tracked point.
     * @param scaleX multiplier for the width of the text.
     * @param scaleY multiplier for the height of the text.
     */
    public void drawString3d(String text, java.awt.Color color, rlbot.vector.Vector3 upperLeft, int scaleX, int scaleY) {

        int colorOffset = Color.createColor(builder, color.getAlpha(), color.getRed(), color.getGreen(), color.getBlue());
        int textOffset = builder.createString(text);

        RenderMessage.startRenderMessage(builder);
        RenderMessage.addRenderType(builder, RenderType.DrawString3D);
        RenderMessage.addColor(builder, colorOffset);
        RenderMessage.addStart(builder, upperLeft.toFlatbuffer(builder));
        RenderMessage.addScaleX(builder, scaleX);
        RenderMessage.addScaleY(builder, scaleY);
        RenderMessage.addText(builder, textOffset);
        int finalOffset = RenderMessage.endRenderMessage(builder);

        renderMessageOffsets.add(finalOffset);
    }
}
