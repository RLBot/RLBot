using rlbot.flat;
using FlatBuffers;

namespace RLBotDotNet.GameState
{
    public class GameInfoState
    {
        public float? GameSpeed;
        public float? WorldGravityZ;
        public bool? Paused;
        public bool? EndMatch;

        public GameInfoState(float? gameSpeed = null, float? worldGravityZ = null, bool? paused = null, bool? endMatch = null)
        {
            GameSpeed = gameSpeed;
            WorldGravityZ = worldGravityZ;
            Paused = paused;
            EndMatch = endMatch;
        }

        public Offset<DesiredGameInfoState> ToFlatBuffer(FlatBufferBuilder builder)
        {
            DesiredGameInfoState.StartDesiredGameInfoState(builder);

            if (GameSpeed.HasValue)
                DesiredGameInfoState.AddGameSpeed(builder, Float.CreateFloat(builder, GameSpeed.Value));

            if (WorldGravityZ.HasValue)
                DesiredGameInfoState.AddWorldGravityZ(builder, Float.CreateFloat(builder, WorldGravityZ.Value));

            if (Paused.HasValue)
                DesiredGameInfoState.AddPaused(builder, Bool.CreateBool(builder, Paused.Value));

            if (EndMatch.HasValue)
                DesiredGameInfoState.AddEndMatch(builder, Bool.CreateBool(builder, EndMatch.Value));

            return DesiredGameInfoState.EndDesiredGameInfoState(builder);
        }
    }
}