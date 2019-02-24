using rlbot.flat;
using FlatBuffers;

namespace RLBotDotNet.GameState
{
    public class GameInfoState
    {
        public float? GameSpeed;
        public float? WorldGravityZ;

        public GameInfoState(float? gameSpeed = null, float? worldGravityZ = null)
        {
            GameSpeed = gameSpeed;
            WorldGravityZ = worldGravityZ;
        }

        public Offset<DesiredGameInfoState> ToFlatBuffer(FlatBufferBuilder builder)
        {
            DesiredGameInfoState.StartDesiredGameInfoState(builder);

            if (GameSpeed.HasValue)
                DesiredGameInfoState.AddGameSpeed(builder, Float.CreateFloat(builder, GameSpeed.Value));

            if (WorldGravityZ.HasValue)
                DesiredGameInfoState.AddWorldGravityZ(builder, Float.CreateFloat(builder, WorldGravityZ.Value));

            return DesiredGameInfoState.EndDesiredGameInfoState(builder);
        }
    }
}
