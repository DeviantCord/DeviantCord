import com.rabbitmq.client.Channel;
import com.rabbitmq.client.Connection;
import com.rabbitmq.client.ConnectionFactory;
import com.rabbitmq.client.DeliverCallback;
import org.json.simple.JSONObject;
import org.json.simple.parser.JSONParser;
import org.json.simple.parser.ParseException;

import java.io.FileReader;
import java.io.IOException;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.concurrent.TimeoutException;

public class testRabbitConsumer {

    public static void main(String[] args) throws IOException, TimeoutException, ParseException {
        JSONParser configparser = new JSONParser();
        Path currentPath = Paths.get(System.getProperty("user.dir"));
        Path rabbitPath = Paths.get(currentPath.toString(),"rabbit.json");
        Object obj = configparser.parse(new FileReader(rabbitPath.toString()));
        JSONObject rabbitJson = (JSONObject) obj;

        ConnectionFactory factory = new ConnectionFactory();
        factory.setUsername(String.valueOf(rabbitJson.get("Username")));
        factory.setHost(String.valueOf(rabbitJson.get("Hostname")));
        factory.setPassword(String.valueOf(rabbitJson.get("Password")));
        String QUEUE = String.valueOf(rabbitJson.get("queue"));

        DeliverCallback deliverCallback = (consumerTag, delivery) -> {
            String message = new String(delivery.getBody(), "UTF-8");
            System.out.println(" [x] Received '" + message + "'");
        };

        Connection connection = factory.newConnection();
        Channel channel = connection.createChannel();
        channel.basicConsume(QUEUE, true, deliverCallback, consumerTag -> { });
    }
}
