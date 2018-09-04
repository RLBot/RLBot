using System.Collections.Generic;
using System.Linq;

using rlbot.flat;
using FlatBuffers;

namespace RLBotDotNet.GameState
{
    public class GameState
    {
        private Dictionary<int, CarState> carStates = new Dictionary<int, CarState>();

        public BallState BallState;
        
        public CarState GetCarState(int index)
        {
            return carStates[index];
        }

        public void SetCarState(int index, CarState carState)
        {
            if (carStates.ContainsKey(index))
                carStates[index] = carState;
            else
                carStates.Add(index, carState);
        }

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

        private static VectorOffset CreateCarStateVector(FlatBufferBuilder builder, Dictionary<int, CarState> carStates)
        {
            int numCars = carStates.Keys.Max() + 1;

            Offset<DesiredCarState>[] carStateOffsets = new Offset<DesiredCarState>[numCars];

            for (int i = 0; i < numCars; i++)
            {
                if (carStates.ContainsKey(i))
                    carStateOffsets[i] = carStates[i].ToFlatBuffer(builder);
                else
                    carStateOffsets[i] = new CarState().ToFlatBuffer(builder);
            }

            return DesiredGameState.CreateCarStatesVector(builder, carStateOffsets);
        }
    }
}
