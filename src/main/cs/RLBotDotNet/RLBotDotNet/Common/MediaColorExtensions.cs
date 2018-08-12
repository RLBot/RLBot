﻿using FlatBuffers;
using rlbot.flat;

namespace RLBotDotNet.Common
{
    /// <summary>
    /// Extension methods for <see cref="System.Windows.Media.Color"/>.
    /// </summary>
    public static class MediaColorExtensions
    {
        /// <summary>
        /// Converts the <see cref="System.Windows.Media.Color"/> to the offset color with the given <see cref="FlatBufferBuilder"/>.
        /// </summary>
        /// <param name="color">The <see cref="System.Windows.Media.Color"/> to convert.</param>
        /// <param name="builder">The <see cref="FlatBufferBuilder"/> to use to create the offset color.</param>
        /// <returns>The created offset color from the <see cref="System.Windows.Media.Color"/>.</returns>
        public static Offset<Color> ToOffsetColor(this System.Windows.Media.Color color, FlatBufferBuilder builder)
        {
            return Color.CreateColor(builder, color.A, color.R, color.G, color.B);
        }
    }
}