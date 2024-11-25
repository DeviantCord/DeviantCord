/*
 * DeviantCord 4
 * Copyright (C) 2020-2024  Errite Softworks LLC/ ErriteEpticRikez
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as published
 * by the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Affero General Public License for more details.
 *
 * You should have received a copy of the GNU Affero General Public License
 * along with this program.  If not, see <https://www.gnu.org/licenses/>.
 */
package org.errite.deviantcord.notifications;

import java.io.IOException;
import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.TimeUnit;

import org.errite.deviantcord.threading.ExecutorManager;
import org.json.simple.JSONObject;
import com.rabbitmq.client.Channel;
import com.rabbitmq.client.Connection;
import com.rabbitmq.client.ConnectionFactory;
import com.rabbitmq.client.DeliverCallback;
import com.rabbitmq.client.Delivery;
import org.javacord.api.DiscordApi;
import io.sentry.Sentry;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.errite.deviantcord.cmds.rabbitRouter;



public class RabbitMQManager {
    private final ExecutorManager executorManager;
    private final ConnectionFactory factory;
    private final String queue;
    private final DiscordApi api;
    private volatile boolean isRunning = true;

    public RabbitMQManager(JSONObject config, ExecutorManager executorManager, DiscordApi api) {
        this.executorManager = executorManager;
        this.factory = createFactory(config);
        this.queue = String.valueOf(config.get("queue"));
        this.api = api;
    }

    private ConnectionFactory createFactory(JSONObject config) {
        ConnectionFactory factory = new ConnectionFactory();
        factory.setHost(String.valueOf(config.get("Hostname")));
        factory.setUsername(String.valueOf(config.get("Username")));
        factory.setPassword(String.valueOf(config.get("Password")));
        factory.setPort(((Long) config.get("Port")).intValue());
        factory.setConnectionTimeout(5000);
        return factory;
    }

    public void start() {
        executorManager.getRabbitExecutor().submit(this::runConsumer);
    }

    public void shutdown() {
        isRunning = false;
    }

    private void runConsumer() {
        while (isRunning) {
            try {
                establishConnection();
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                break;
            } catch (Exception e) {
                handleError("RabbitMQ connection error", e);
                if (isRunning) {
                    sleepBeforeRetry();
                }
            }
        }
    }

    private void establishConnection() throws Exception {
        try (Connection connection = factory.newConnection();
             Channel channel = connection.createChannel()) {
            
            setupChannel(channel);
            
            while (isRunning && connection.isOpen()) {
                TimeUnit.SECONDS.sleep(5);
            }
        }
    }

    private void setupChannel(Channel channel) throws IOException {
        Map<String, Object> arguments = new HashMap<>();
        arguments.put("x-queue-type", "quorum");
        
        channel.queueDeclare(queue, true, false, false, arguments);
        channel.basicQos(1);
        
        DeliverCallback deliverCallback = (consumerTag, delivery) -> {
            handleMessage(channel, delivery);
        };
        
        channel.basicConsume(queue, false, deliverCallback, 
            consumerTag -> System.out.printf("Consumer cancelled: %s%n", consumerTag));
    }

    private void handleMessage(Channel channel, Delivery delivery) {
        try {
            String message = new String(delivery.getBody(), "UTF-8");
            rabbitRouter.routeMessage(message, api);
            channel.basicAck(delivery.getEnvelope().getDeliveryTag(), false);
        } catch (Exception e) {
            handleMessageError(channel, delivery, e);
        }
    }

    private void handleMessageError(Channel channel, Delivery delivery, Exception e) {
        try {
            channel.basicNack(delivery.getEnvelope().getDeliveryTag(), false, true);
            handleError("Message processing error", e);
        } catch (IOException ioe) {
            handleError("Error sending NACK", ioe);
        }
    }

    private void handleError(String message, Exception e) {
        String eventId = Sentry.captureException(e).toString();
        System.out.printf("Error logged with ID: %s%n", eventId);
    }

    private void sleepBeforeRetry() {
        try {
            TimeUnit.SECONDS.sleep(5);
        } catch (InterruptedException ie) {
            Thread.currentThread().interrupt();
        }
    }
}