using System.Collections.Generic;
using System.Linq;

using rlbot.flat;
using FlatBuffers;

namespace RLBotDotNet.GameState
{
    public class GameState
    {
        private Dictionary<int, CarState> carStates = new Dictionary<int, CarState>();

        private BallState ballState;

        public BallState BallState
        {
            get
            {
                if (ballState == null)
                    ballState = new BallState();

                return ballState;
            }

            set
            {
                ballState = value;
            }
        }

        public CarState GetCarState(int index)
        {
            if (!carStates.ContainsKey(index))
                carStates.Add(index, new CarState());

            return carStates[index];
        }

        public void SetCarState(int index, CarState carState)
        {
            if (carStates.ContainsKey(index))
                carStates[index] = carState;
            else
                carStates.Add(index, carState);
        }

        /// <summary>
        /// Builds the flatbuffer containing the desired state.
        /// This is only used internally.
        /// </summary>
        /// <returns></returns>
        public GameStatePacket BuildGameStatePacket()
        {
            FlatBufferBuilder builder = new FlatBufferBuilder(100);

            int ballStateOffset = -1;
            
            if (BallState != null)
                ballStateOffset = BallState.ToFlatBuffer(builder).Value;

            VectorOffset carStateVector = CreateCarStateVector(builder, carStates);

            DesiredGameState.StartDesiredGameState(builder);

            if (BallState != null)
                DesiredGameState.AddBallState(builder, new Offset<DesiredBallState>(ballStateOffset));

            DesiredGameState.AddCarStates(builder, carStateVector);

            builder.Finish(DesiredGameState.EndDesiredGameState(builder).Value);

            return new GameStatePacket(builder.SizedByteArray());
        }

        /// <summary>
        /// Creates a GameState from a GameTickPacket. Usefull for saving a scenario.
        /// </summary>
        /// <param name="gameTickPacket">The packet to create the GameState from.</param>
        /// <returns></returns>
        public static GameState CreateFromGameTickPacket(GameTickPacket gameTickPacket)
        {
            GameState gameState = new GameState();

            if (gameTickPacket.Ball.HasValue)
            {
                gameState.BallState = new BallState(gameTickPacket.Ball.Value);
            }

            for (int i = 0; i < gameTickPacket.PlayersLength; i++)
            {
                if (gameTickPacket.Players(i).HasValue)
                {
                    gameState.SetCarState(i, new CarState(gameTickPacket.Players(i).Value));
                }
            }

            return gameState;
        }

        private static VectorOffset CreateCarStateVector(FlatBufferBuilder builder, Dictionary<int, CarState> carStates)
        {
            if (carStates.Count == 0)
                return DesiredGameState.CreateCarStatesVector(builder, new Offset<DesiredCarState>[0]);

            int numCars = carStates.Keys.Max() + 1;

            Offset<DesiredCarState>[] carStateOffsets = new Offset<DesiredCarState>[numCars];

            for (int i = 0; i < numCars; i++)
            {
                if (carStates.ContainsKey(i) && carStates[i] != null)
                    carStateOffsets[i] = carStates[i].ToFlatBuffer(builder);
                else
                    carStateOffsets[i] = new CarState().ToFlatBuffer(builder);
            }

            return DesiredGameState.CreateCarStatesVector(builder, carStateOffsets);
        }
    }
}
