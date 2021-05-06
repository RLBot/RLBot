using System;
using RLBotDotNet;
using RLBotDotNet.GameState;
using rlbot.flat;
using Color = System.Drawing.Color;

namespace TestBot
{
    // We want to our bot to derive from Bot, and then implement its abstract methods.
    class ExampleBot : Bot
    {
        // We want the constructor for ExampleBot to extend from Bot, but we don't want to add anything to it.
        public ExampleBot(string botName, int botTeam, int botIndex) : base(botName, botTeam, botIndex) { }

        public override Controller GetOutput(GameTickPacket gameTickPacket)
        {
            // This controller object will be returned at the end of the method.
            // This controller will contain all the inputs that we want the bot to perform.
            Controller controller = new Controller();

            // Wrap gameTickPacket retrieving in a try-catch so that the bot doesn't crash whenever a value isn't present.
            // A value may not be present if it was not sent.
            // These are nullables so trying to get them when they're null will cause errors, therefore we wrap in try-catch.
            try
            {
                // Store the required data from the gameTickPacket.
                Vector3 ballLocation = gameTickPacket.Ball.Value.Physics.Value.Location.Value;
                Vector3 carLocation = gameTickPacket.Players(this.Index).Value.Physics.Value.Location.Value;
                Rotator carRotation = gameTickPacket.Players(this.Index).Value.Physics.Value.Rotation.Value;

                // Calculate to get the angle from the front of the bot's car to the ball.
                double botToTargetAngle = Math.Atan2(ballLocation.Y - carLocation.Y, ballLocation.X - carLocation.X);
                double botFrontToTargetAngle = botToTargetAngle - carRotation.Yaw;
                // Correct the angle
                if (botFrontToTargetAngle < -Math.PI)
                    botFrontToTargetAngle += 2 * Math.PI;
                if (botFrontToTargetAngle > Math.PI)
                    botFrontToTargetAngle -= 2 * Math.PI;

                // Decide which way to steer in order to get to the ball.
                if (botFrontToTargetAngle > 0)
                    controller.Steer = 1;
                else
                    controller.Steer = -1;

                Renderer.DrawLine3D(Color.FromArgb(255, 255, 0), ballLocation, carLocation);

                // Get the ball prediction data.
                BallPrediction prediction = GetBallPrediction();

                // Loop through every 10th point so we don't render too many lines.
                for (int i = 10; i < prediction.SlicesLength; i += 10)
                {
                    Vector3 pointA = prediction.Slices(i - 10).Value.Physics.Value.Location.Value;
                    Vector3 pointB = prediction.Slices(i).Value.Physics.Value.Location.Value;

                    Renderer.DrawLine3D(Color.FromArgb(255, 0, 255), pointA, pointB);
                }

                // Test out setting game state
                GameState gameState = new GameState();

                // Make the ball hover in midair
                gameState.BallState.PhysicsState = new PhysicsState(location: new DesiredVector3(z: 300), velocity: new DesiredVector3(z: 10));

                // If the ball stops moving, fling the car at it
                Vector3 ballVelocity = gameTickPacket.Ball.Value.Physics.Value.Velocity.Value;
                if (ballVelocity.X * ballVelocity.X + ballVelocity.Y * ballVelocity.Y < 100000 && carLocation.Z < 100)
                {
                    PhysicsState carPhysicsState = gameState.GetCarState(Index).PhysicsState;
                    carPhysicsState.Location = new DesiredVector3(ballLocation.X - 300, ballLocation.Y, 400);
                    carPhysicsState.Velocity = new DesiredVector3(500, 0, 0);

                    if (gameTickPacket.Ball?.LatestTouch?.PlayerIndex is int playerIndex)
                    {
                        Console.WriteLine("Latest touch by " + playerIndex);
                    }

                    MatchSettings matchSettings = GetMatchSettings();
                    Console.WriteLine("Map: " + matchSettings.GameMap);
                }

                SetGameState(gameState);
            }
            catch (Exception e)
            {
                Console.WriteLine(e.Message);
                Console.WriteLine(e.StackTrace);
            }

            // Set the throttle to 1 so the bot can move.
            controller.Throttle = 1;

            controller.UseItem = controller.Steer > 0; // Spam items

            return controller;
        }

        public override void Dispose()
        {
            // This bot doesn't initialize any resources that cannot be automatically released by the managed runtime (threads, various IDisposables, etc.).
            // If it did, then it would release them here.
        }
    }
}
