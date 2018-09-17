using System;
using System.Collections.Generic;
using System.Numerics;
using FlatBuffers;
using rlbot.flat;
using RLBotDotNet.Common;
using RLBotDotNet.Utils;
using Color = System.Windows.Media.Color;
using Vector3 = System.Numerics.Vector3;

namespace RLBotDotNet.Renderer
{
    /// <summary>
    /// Base Renderer used to draw in the game.
    /// </summary>
    public abstract class Renderer
    {
        private readonly int _index;
        private readonly List<Offset<RenderMessage>> _renderMessageOffsets;

        /// <summary>
        /// Constructs a new instance of Renderer with the index of the renderer.
        /// </summary>
        /// <param name="index">The index of the renderer.</param>
        protected Renderer(int index)
        {
            _renderMessageOffsets = new List<Offset<RenderMessage>>();
            _index = index;
        }

        /// <summary>
        /// Gets and sets the FlatBufferBuilder used to build the render messages.
        /// </summary>
        protected FlatBufferBuilder Builder { get; set; }
        
        /// <summary>
        /// Removes any draw calls that have been queued up and starts over.
        /// Can be called at any time.
        /// </summary>
        public void ResetPacket()
        {
            Builder = null;
            _renderMessageOffsets.Clear();
        }

        /// <summary>
        /// If this renderer has previously drawn anything on the screen, it will be erased.
        /// This can be called at any time. It will not interrupt any packet construction
        /// that may be in progress.
        /// </summary>
        public void EraseFromScreen()
        {
            var eraseBuilder = new FlatBufferBuilder(10);
            var vectorOffset = RenderGroup.CreateRenderMessagesVector(eraseBuilder, new Offset<RenderMessage>[0]);
            RenderGroup.StartRenderGroup(eraseBuilder);
            RenderGroup.AddRenderMessages(eraseBuilder, vectorOffset);
            RenderGroup.AddId(eraseBuilder, _index);
            eraseBuilder.Finish(RenderGroup.EndRenderGroup(eraseBuilder).Value);

            RenderPacket emptyPacket = new RenderPacket(eraseBuilder.SizedByteArray());
            SendPacket(emptyPacket);
        }

        /// <summary>
        /// Returns true if any draw calls have been queued up for the current packet.
        /// </summary>
        /// <returns></returns>
        public bool HasContent()
        {
            return Builder != null && Builder.Offset > 0;
        }

        /// <summary>
        /// Draws a line in screen coordinates.
        /// </summary>
        /// <param name="color">The color of the line.</param>
        /// <param name="start">The start point of the line.</param>
        /// <param name="end">The end point of the line.</param>
        public void DrawLine2D(Color color, Vector2 start, Vector2 end)
        {

            var colorOffset = color.ToOffsetColor(Builder);

            RenderMessage.StartRenderMessage(Builder);
            RenderMessage.AddRenderType(Builder, RenderType.DrawLine2D);
            RenderMessage.AddColor(Builder, colorOffset);
            RenderMessage.AddStart(Builder, start.ToOffsetVector(Builder));
            RenderMessage.AddEnd(Builder, end.ToOffsetVector(Builder));
            var finalOffset = RenderMessage.EndRenderMessage(Builder);

            _renderMessageOffsets.Add(finalOffset);
        }

        /// <summary>
        /// Draws a polyline between screen coordinates.
        /// </summary>
        /// <param name="color">The color of the line.</param>
        /// <param name="vectors">The vectors of the line.</param>
        public void DrawPolyLine2D(Color color, Vector2[] vectors)
        {
            if (vectors.Length < 2)
            {
                throw new ArgumentException("DrawPolyLine2D: Vectors array must contain atleast 2 vectors!");
            }

            var colorOffset = color.ToOffsetColor(Builder);

            for (int i = 0; i < vectors.Length-1; i++)
            {
                RenderMessage.StartRenderMessage(Builder);
                RenderMessage.AddRenderType(Builder, RenderType.DrawLine2D);
                RenderMessage.AddColor(Builder, colorOffset);
                RenderMessage.AddStart(Builder, vectors[i].ToOffsetVector(Builder));
                RenderMessage.AddEnd(Builder, vectors[i+1].ToOffsetVector(Builder));
                var finalOffset = RenderMessage.EndRenderMessage(Builder);
                _renderMessageOffsets.Add(finalOffset);
            }
        }

        /// <summary>
        /// Draws a line between two 3D coordinates.
        /// </summary>
        /// <param name="color">The color of the line.</param>
        /// <param name="start">The start point of the line.</param>
        /// <param name="end">The end point of the line.</param>
        public void DrawLine3D(Color color, Vector3 start, Vector3 end)
        {

            var colorOffset = color.ToOffsetColor(Builder);

            RenderMessage.StartRenderMessage(Builder);
            RenderMessage.AddRenderType(Builder, RenderType.DrawLine3D);
            RenderMessage.AddColor(Builder, colorOffset);
            RenderMessage.AddStart(Builder, start.ToOffsetVector(Builder));
            RenderMessage.AddEnd(Builder, end.ToOffsetVector(Builder));
            var finalOffset = RenderMessage.EndRenderMessage(Builder);

            _renderMessageOffsets.Add(finalOffset);
        }

        /// <summary>
        /// Draws a polyline between 3D coordinates.
        /// </summary>
        /// <param name="color">The color of the line.</param>
        /// <param name="vectors">The vectors of the line.</param>
        public void DrawPolyLine3D(Color color, Vector3[] vectors)
        {
            if (vectors.Length < 2)
            {
                throw new ArgumentException("DrawPolyLine3D: Vectors array must contain atleast 2 vectors!");
            }

            var colorOffset = color.ToOffsetColor(Builder);

            for (int i = 0; i < vectors.Length - 1; i++)
            {
                RenderMessage.StartRenderMessage(Builder);
                RenderMessage.AddRenderType(Builder, RenderType.DrawLine3D);
                RenderMessage.AddColor(Builder, colorOffset);
                RenderMessage.AddStart(Builder, vectors[i].ToOffsetVector(Builder));
                RenderMessage.AddEnd(Builder, vectors[i + 1].ToOffsetVector(Builder));
                var finalOffset = RenderMessage.EndRenderMessage(Builder);
                _renderMessageOffsets.Add(finalOffset);
            }
        }

        /// <summary>
        /// Draws a line between two 3D coordinates.
        /// </summary>
        /// <param name="color">The color of the line.</param>
        /// <param name="start">The start point of the line.</param>
        /// <param name="end">The end point of the line.</param>
        public void DrawLine3D(Color color, rlbot.flat.Vector3 start, rlbot.flat.Vector3 end)
        {
            DrawLine3D(color, new Vector3(start.X, start.Y, start.Z), new Vector3(end.X, end.Y, end.Z));
        }

        /// <summary>
        /// Draws a polyline between 3D coordinates.
        /// </summary>
        /// <param name="color">The color of the line.</param>
        /// <param name="vectors">The vectors of the line.</param>
        public void DrawPolyLine3D(Color color, rlbot.flat.Vector3[] vectors)
        {
            Vector3[] outVectors = new Vector3[vectors.Length];
            for (int i = 0; i < vectors.Length; i++)
            {
                outVectors[i] = new Vector3(vectors[i].X, vectors[i].Y, vectors[i].Z);
            }
            DrawPolyLine3D(color, outVectors);
        }

        /// <summary>
        /// Draws a 2D line which starts at screen coordinates and ends at a 3D coordinate.
        /// </summary>
        /// <param name="color">The color of the line.</param>
        /// <param name="start">The start point of the line.</param>
        /// <param name="end">The end point of the line.</param>
        public void DrawLine2D3D(Color color, Vector2 start, Vector3 end)
        {

            var colorOffset = color.ToOffsetColor(Builder);

            RenderMessage.StartRenderMessage(Builder);
            RenderMessage.AddRenderType(Builder, RenderType.DrawLine2D_3D);
            RenderMessage.AddColor(Builder, colorOffset);
            RenderMessage.AddStart(Builder, start.ToOffsetVector(Builder));
            RenderMessage.AddEnd(Builder, end.ToOffsetVector(Builder));
            var finalOffset = RenderMessage.EndRenderMessage(Builder);

            _renderMessageOffsets.Add(finalOffset);
        }

        /// <summary>
        /// Draws a 2D line which starts at screen coordinates and ends at a 3D coordinate.
        /// </summary>
        /// <param name="color">The color of the line.</param>
        /// <param name="start">The start point of the line.</param>
        /// <param name="end">The end point of the line.</param>
        public void DrawLine2D3D(Color color, Vector2 start, rlbot.flat.Vector3 end)
        {
            DrawLine2D3D(color, start, new Vector3(end.X, end.Y, end.Z));
        }

        /// <summary>
        /// This draws a 2D rectangle in screen coordinates.
        /// </summary>
        /// <param name="color">The color of the rectangle.</param>
        /// <param name="upperLeft">The upper left corner of the rectangle.</param>
        /// <param name="width">The width in pixels.</param>
        /// <param name="height">The height in pixels</param>
        /// <param name="filled">Flag indicating whether the rectangle should be filled in</param>
        public void DrawRectangle2D(Color color, Vector2 upperLeft, int width, int height, bool filled)
        {

            var colorOffset = color.ToOffsetColor(Builder);

            RenderMessage.StartRenderMessage(Builder);
            RenderMessage.AddRenderType(Builder, RenderType.DrawRect2D);
            RenderMessage.AddColor(Builder, colorOffset);
            RenderMessage.AddStart(Builder, upperLeft.ToOffsetVector(Builder));
            RenderMessage.AddScaleX(Builder, width);
            RenderMessage.AddScaleY(Builder, height);
            RenderMessage.AddIsFilled(Builder, filled);
            var finalOffset = RenderMessage.EndRenderMessage(Builder);

            _renderMessageOffsets.Add(finalOffset);
        }
        
        /// <summary>
        /// This draws a 2D rectangle at a 3D-tracked position.
        /// </summary>
        /// <param name="color">The color of the rectangle.</param>
        /// <param name="upperLeft">The upper left corner of the rectangle.</param>
        /// <param name="width">The width in pixels.</param>
        /// <param name="height">The height in pixels</param>
        /// <param name="filled">Flag indicating whether the rectangle should be filled in</param>
        public void DrawRectangle3D(Color color, Vector3 upperLeft, int width, int height, bool filled)
        {
            DrawRect3D(color, upperLeft, width, height, filled, false);
        }

        /// <summary>
        /// This draws a 2D rectangle at a 3D-tracked position.
        /// </summary>
        /// <param name="color">The color of the rectangle.</param>
        /// <param name="upperLeft">The upper left corner of the rectangle.</param>
        /// <param name="width">The width in pixels.</param>
        /// <param name="height">The height in pixels</param>
        /// <param name="filled">Flag indicating whether the rectangle should be filled in</param>
        public void DrawRectangle3D(Color color, rlbot.flat.Vector3 position, int width, int height, bool filled)
        {
            DrawRectangle3D(color, new Vector3(position.X, position.Y, position.Z), width, height, filled);
        }

        /// <summary>
        /// This draws a 2D rectangle at a 3D-tracked position.
        /// </summary>
        /// <param name="color">The color of the rectangle.</param>
        /// <param name="position">The center of the rectangle.</param>
        /// <param name="width">The width in pixels.</param>
        /// <param name="height">The height in pixels</param>
        /// <param name="filled">Flag indicating whether the rectangle should be filled in</param>
        public void DrawCenteredRectangle3D(Color color, Vector3 position, int width, int height, bool filled)
        {
            DrawRect3D(color, position, width, height, filled, true);
        }

        /// <summary>
        /// This draws a 2D rectangle at a 3D-tracked position.
        /// </summary>
        /// <param name="color">The color of the rectangle.</param>
        /// <param name="position">The center of the rectangle.</param>
        /// <param name="width">The width in pixels.</param>
        /// <param name="height">The height in pixels</param>
        /// <param name="filled">Flag indicating whether the rectangle should be filled in</param>
        public void DrawCenteredRectangle3D(Color color, rlbot.flat.Vector3 position, int width, int height, bool filled)
        {
            DrawCenteredRectangle3D(color, new Vector3(position.X, position.Y, position.Z), width, height, filled);
        }

        private void DrawRect3D(Color color, Vector3 position, int width, int height, bool filled, bool centered)
        {
            var colorOffset = color.ToOffsetColor(Builder);
            RenderMessage.StartRenderMessage(Builder);
            RenderMessage.AddRenderType(Builder, centered ? RenderType.DrawCenteredRect3D : RenderType.DrawRect3D);
            RenderMessage.AddColor(Builder, colorOffset);
            RenderMessage.AddStart(Builder, position.ToOffsetVector(Builder));
            RenderMessage.AddScaleX(Builder, width);
            RenderMessage.AddScaleY(Builder, height);
            RenderMessage.AddIsFilled(Builder, filled);
            var finalOffset = RenderMessage.EndRenderMessage(Builder);

            _renderMessageOffsets.Add(finalOffset);
        }
        
        /// <summary>
        /// Draws a string in screen coordinates.
        /// </summary>
        /// <param name="text">The text to draw.</param>
        /// <param name="color">The color of the string.</param>
        /// <param name="upperLeft">The location of the upper left corner of the text.</param>
        /// <param name="scaleX">The multiplier for the width of the text.</param>
        /// <param name="scaleY">The multiplier for the height of the text</param>
        public void DrawString2D(String text, Color color, Vector2 upperLeft, int scaleX, int scaleY)
        {

            var colorOffset = color.ToOffsetColor(Builder);
            var textOffset = Builder.CreateString(text);

            RenderMessage.StartRenderMessage(Builder);
            RenderMessage.AddRenderType(Builder, RenderType.DrawString2D);
            RenderMessage.AddColor(Builder, colorOffset);
            RenderMessage.AddStart(Builder, upperLeft.ToOffsetVector(Builder));
            RenderMessage.AddScaleX(Builder, scaleX);
            RenderMessage.AddScaleY(Builder, scaleY);
            RenderMessage.AddText(Builder, textOffset);
            var finalOffset = RenderMessage.EndRenderMessage(Builder);

            _renderMessageOffsets.Add(finalOffset);
        }
        
        /// <summary>
        /// Draws a string in 2D, but the upper-left corner is at a 3D-tracked point.
        /// </summary>
        /// <param name="text">The text to draw.</param>
        /// <param name="color">The color of the string.</param>
        /// <param name="upperLeft">The location of the upper left corner of the text.</param>
        /// <param name="scaleX">The multiplier for the width of the text.</param>
        /// <param name="scaleY">The multiplier for the height of the text</param>
        public void DrawString3D(String text, Color color, Vector3 upperLeft, int scaleX, int scaleY)
        {

            var colorOffset = color.ToOffsetColor(Builder);
            var textOffset = Builder.CreateString(text);

            RenderMessage.StartRenderMessage(Builder);
            RenderMessage.AddRenderType(Builder, RenderType.DrawString3D);
            RenderMessage.AddColor(Builder, colorOffset);
            RenderMessage.AddStart(Builder, upperLeft.ToOffsetVector(Builder));
            RenderMessage.AddScaleX(Builder, scaleX);
            RenderMessage.AddScaleY(Builder, scaleY);
            RenderMessage.AddText(Builder, textOffset);
            var finalOffset = RenderMessage.EndRenderMessage(Builder);

            _renderMessageOffsets.Add(finalOffset);
        }

        /// <summary>
        /// Draws a string in 2D, but the upper-left corner is at a 3D-tracked point.
        /// </summary>
        /// <param name="text">The text to draw.</param>
        /// <param name="color">The color of the string.</param>
        /// <param name="upperLeft">The location of the upper left corner of the text.</param>
        /// <param name="scaleX">The multiplier for the width of the text.</param>
        /// <param name="scaleY">The multiplier for the height of the text</param>
        public void DrawString3D(String text, Color color, rlbot.flat.Vector3 upperLeft, int scaleX, int scaleY)
        {
            DrawString3D(text, color, new Vector3(upperLeft.X, upperLeft.Y, upperLeft.Z), scaleX, scaleY);
        }

        /// <summary>
        /// Sends the render packet to the RL Bot interface.
        /// </summary>
        /// <param name="packet">The packet to send.</param>
        protected void SendPacket(RenderPacket packet)
        {
            RLBotInterface.RenderPacket(packet);
        }

        /// <summary>
        /// Finishes the render packet and returns the complete packet.
        /// </summary>
        /// <returns>Returns the completed render packet.</returns>
        protected RenderPacket DoFinishPacket()
        {

            var offsets = _renderMessageOffsets.ToArray();
            var messagesOffset = RenderGroup.CreateRenderMessagesVector(Builder, offsets);
            var renderGroupOffset = RenderGroup.CreateRenderGroup(Builder, messagesOffset, _index);

            Builder.Finish(renderGroupOffset.Value);
            var bytes = Builder.SizedByteArray();

            ResetPacket();
            return new RenderPacket(bytes);
        }
    }
}