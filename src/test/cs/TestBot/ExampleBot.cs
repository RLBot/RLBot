using System;
using RLBotDotNet;
using rlbot.flat;
using Color = System.Windows.Media.Color;

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
                Vector3 carLocation = gameTickPacket.Players(this.index).Value.Physics.Value.Location.Value;
                Rotator carRotation = gameTickPacket.Players(this.index).Value.Physics.Value.Rotation.Value;

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

                Renderer.DrawLine3D(Color.FromRgb(255, 255, 0),
                    new System.Numerics.Vector3(ballLocation.X, ballLocation.Y, ballLocation.Z),
                    new System.Numerics.Vector3(carLocation.X, carLocation.Y, carLocation.Z));

                // controller.Steer = 0;

            }
            catch (Exception e)
            {
                Console.WriteLine(e.Message);
                Console.WriteLine(e.StackTrace);
            }

            // Set the throttle to 1 so the bot can move.
            controller.Throttle = 1;

            return controller;
        }
    }
}
