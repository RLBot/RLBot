To run this agent:

1. Install Java 8.
2. Run `pip install grpcio` on the command line (one time setup).
3. Modify rlbot.cfg to reference java_demo_agent.cfg.
4. Open a terminal and navigate to `./agents/java_demo`, then execute `./gradlew.bat run`.
5. Open another terminal and execute `python runner.py`.


IntelliJ IDEA is recommended for Java development. To get started using it:
1. Open a terminal and navigate to `./agents/java_demo`, then execute `./gradlew.bat idea`.
2. Open IntelliJ, and open the `java_demo.iml` file which should now be present in that directory.
3. To run the GrpcServer, you can right click on src/rlbot/GrpcServer and choose Run or Debug.