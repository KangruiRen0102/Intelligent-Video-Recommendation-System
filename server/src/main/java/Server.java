import com.sun.net.httpserver.HttpServer;

import java.util.Scanner;
import java.io.IOException;
import java.io.PrintWriter;
import java.net.InetAddress;
import java.net.InetSocketAddress;

public class Server {
  public static void main(String[] args) throws IOException {

    int port = 8082;
    String pathToInference = "<AbsolutePathToInference.Py";
    System.out.printf("Starting server at %s:%d%n", InetAddress.getLocalHost().getHostName(), port);

    HttpServer server = HttpServer.create(new InetSocketAddress(port), 0);
    server.createContext(
            "/recommend",
            httpExchange -> {
              httpExchange.getResponseHeaders().add("Content-Type", "text/html");
              httpExchange.sendResponseHeaders(200, 0);
              String uri = httpExchange.getRequestURI().getPath();
              String userId = uri.substring(uri.lastIndexOf('/') + 1);
              PrintWriter response = new PrintWriter(httpExchange.getResponseBody());
              System.out.printf("Received recommendation request for user %s%n", userId);

              // ==================
              // Recommendation system inference

              ProcessBuilder processBuilder = new ProcessBuilder("python3", pathToInference, userId);
              processBuilder.redirectErrorStream(false);

              Process process = processBuilder.start();
              Scanner s = new Scanner(process.getInputStream()).useDelimiter("\\A");
              String recommendations = s.hasNext() ? s.next() : "";

              // ==================

              response.printf(recommendations);
              response.close();
              System.out.printf("Recommended watchlist for user %s: %s%n", userId, recommendations);
            });
    server.start();
  }
}
