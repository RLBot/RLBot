package rlbot;

import io.grpc.Server;
import io.grpc.ServerBuilder;

import javax.swing.*;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Optional;
import java.util.stream.Stream;

public class GrpcServer {

    private static int port;
    private final Server server;

    private GrpcServer() throws IOException {
        server = ServerBuilder.forPort(port).addService(new GrpcService()).build();
    }

    /** Start serving requests. */
    private void start() throws IOException {
        server.start();
        Runtime.getRuntime().addShutdownHook(new Thread(() -> {
            // Use stderr here since the logger may has been reset by its JVM shutdown hook.
            System.err.println("*** shutting down gRPC server since JVM is shutting down");
            GrpcServer.this.stop();
            System.err.println("*** server shut down");
        }));
    }

    /** Stop serving requests and shutdown resources. */
    private void stop() {
        if (server != null) {
            server.shutdown();
        }
    }

    /**
     * Await termination on the main thread since the grpc library uses daemon threads.
     */
    private void blockUntilShutdown() throws InterruptedException {
        if (server != null) {
            server.awaitTermination();
        }
    }

    /**
     * Main method.  This comment makes the linter happy.
     */
    public static void main(String[] args) throws Exception {

        try {
            UIManager.setLookAndFeel(UIManager.getSystemLookAndFeelClassName());
        } catch (Exception e) {
            e.printStackTrace();
        }

        port = readPortFromFile();

        GrpcServer server = new GrpcServer();
        server.start();

        System.out.println(String.format("Grpc server started on port %s. Listening for Rocket League data!", port));

        server.blockUntilShutdown();
    }

    private static Integer readPortFromFile() {
        Path path = Paths.get("port.cfg");

        try (Stream<String> lines = Files.lines(path)) {
            Optional<String> firstLine = lines.findFirst();
            return firstLine.map(Integer::parseInt).orElseThrow(() -> new RuntimeException("Port config file was empty!"));
        } catch (final IOException e) {
            throw new RuntimeException("Failed to read port file! Tried to find it at " + path.toAbsolutePath().toString());
        }
    }
}
