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
package org.errite.deviantcord;

import com.zaxxer.hikari.HikariConfig;
import com.zaxxer.hikari.HikariDataSource;
import io.restassured.response.Response;
import io.sentry.Sentry;

import org.errite.deviantcord.cache.RedisConfig;
import org.errite.deviantcord.cmds.*;
import org.errite.deviantcord.dls.DlsParser;
import org.errite.deviantcord.psql.SQLManager;
import org.errite.deviantcord.types.DeviantRole;
import org.javacord.api.DiscordApi;
import org.javacord.api.DiscordApiBuilder;
import org.javacord.api.Javacord;
import org.javacord.api.entity.server.Server;
import org.javacord.api.event.server.ServerJoinEvent;
import org.javacord.api.event.server.ServerLeaveEvent;
import org.javacord.api.interaction.*;
import org.javacord.api.listener.server.ServerJoinListener;
import org.javacord.api.listener.server.ServerLeaveListener;
import org.json.simple.JSONObject;
import org.json.simple.parser.JSONParser;
import org.errite.deviantcord.da.daParser;
import org.errite.deviantcord.notifications.RabbitMQManager;
import org.errite.deviantcord.notifications.notificationManager;
import redis.clients.jedis.JedisPool;
import redis.clients.jedis.JedisPoolConfig;
import redis.clients.jedis.Protocol;
import com.rabbitmq.client.ConnectionFactory;
import com.rabbitmq.client.Channel;
import com.rabbitmq.client.DeliverCallback;
import java.io.FileWriter;
import java.io.BufferedWriter;
import java.util.Map;



import java.io.FileReader;
import java.io.IOException;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.sql.*;
import java.time.Duration;
import java.util.Arrays;
import java.util.HashMap;
import java.util.Locale;
import java.util.Properties;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicReference;
import java.util.function.Consumer;

import com.zaxxer.hikari.HikariPoolMXBean;

import org.javacord.api.entity.intent.Intent;

import java.util.concurrent.atomic.AtomicInteger;
import org.javacord.api.entity.message.MessageFlag;

import org.errite.deviantcord.threading.ExecutorManager;
import org.errite.deviantcord.health.DatabaseHealthManager;
import org.errite.deviantcord.notifications.RabbitMQManager;
import org.errite.deviantcord.util.configreader;
import org.errite.deviantcord.cmds.CommandHandler;

import org.errite.deviantcord.cache.RedisConfig;
public class DeviantCordBot {

    // Add at class level with other static variables
    private static Path rabbitConfigPath;
    private static RabbitMQManager rabbitManager;
    private static ExecutorManager executorManager;
    private static DatabaseHealthManager healthManager;

    //ATOMICReferences can be modified on any thread!
    public static AtomicReference<String> da_token = new AtomicReference<String>();
    public static AtomicReference<String> dls_token = new AtomicReference<String>();
    public static HashMap<Long, DeviantRole> deviant_roleids = new HashMap<>();
    public static JedisPool pool;
    public static DiscordApi api;
    public static HikariDataSource ds;
    public static String da_secret = "placeholder";
    public static String da_id = "placeholder";
    JedisPool jedisPool;
    
    private static void initializeRabbitMQ() {
        try {
            JSONObject rabbitConfig = configreader.readConfig(rabbitConfigPath);
            rabbitManager = new RabbitMQManager(rabbitConfig, executorManager, api);
            rabbitManager.start();
            System.out.println("RabbitMQ initialization complete");
        } catch (Exception e) {
            String eventId = Sentry.captureException(e).toString();
            System.out.println("RabbitMQ initialization failed with ID: " + eventId);
        }
    }

    
    static {
        executorManager = new ExecutorManager();
        
        // Schedule health checks
        executorManager.getHealthCheckExecutor().scheduleWithFixedDelay(
            () -> healthManager.checkHealth(),
            30, 30, TimeUnit.SECONDS
        );
        
        // Add shutdown hook
        Runtime.getRuntime().addShutdownHook(new Thread(executorManager::shutdown));
    }

    

    public static void main(String[] args) {
        System.out.println("NOTE: THIS IS AN TESTING BUILD, ");
        System.out.println("DeviantCord Beta-V4.0.10");
        System.out.println("Developed by Errite Softworks LLC, 2024");
        System.out.println("Current Javacord Version " + Javacord.VERSION);
        JSONParser configparser = new JSONParser();
        System.out.println("Reading Configs");
        Path currentPath = Paths.get(System.getProperty("user.dir"));
        Path dbConfigPath = Paths.get(currentPath.toString(),"db.json");
        Path globalConfigPath = Paths.get(currentPath.toString(),"config.json");
        Path clientConfigPath = Paths.get(currentPath.toString(),"client.json");
        rabbitConfigPath = Paths.get(currentPath.toString(),"rabbit.json");
        System.out.println(dbConfigPath.toString());

        String token = "placeholder";
        try {
            Object mainconfObj = configparser.parse(new FileReader(globalConfigPath.toString()));
            JSONObject mainconfJsonObject = (JSONObject) mainconfObj;
            boolean use_sentry = (boolean) mainconfJsonObject.get("use_sentry");
            if(use_sentry)
            {
                System.out.println("\nStarting Sentry...");
                Sentry.init(options -> {
                    options.setDsn((String) mainconfJsonObject.get("sentry_dsn"));
                    // Set tracesSampleRate to 1.0 to capture 100% of transactions for performance monitoring.
                    // We recommend adjusting this value in production.
                    options.setTracesSampleRate(1.0);
                    options.setEnvironment("production");
                });
            }
            Object obj = configparser.parse(new FileReader(dbConfigPath.toString()));
            JSONObject jsonObject = (JSONObject) obj;
            String host = (String) jsonObject.get("database-host");
            String username = (String) jsonObject.get("database-username");
            String password = (String) jsonObject.get("database-password");
            String port = String.valueOf(jsonObject.get("database-port"));
            String database_name = (String) jsonObject.get("database-name");
            String redis_host = (String) jsonObject.get("redis_host");
            String redis_password = (String) jsonObject.get("redis_password");
            String redis_username = (String) jsonObject.get("redis_username");
            int redis_port = ((Long) jsonObject.get("redis_port")).intValue();
            Properties props = new Properties();


            props.setProperty("dataSourceClassName", "org.postgresql.ds.PGSimpleDataSource");
            String url = "jdbc:postgresql://" + host + ":" + port + "/" + database_name;
            props.setProperty("dataSource.url", url);
            props.setProperty("dataSource.user", username);
            props.setProperty("dataSource.password", password);
            HikariConfig config = new HikariConfig(props);

            // Adjust connection pool settings for better reliability
            config.setMaximumPoolSize(20);                // Increase from default
            config.setMinimumIdle(5);                     // Maintain some idle connections
            config.setKeepaliveTime(300000);              // 5 minutes
            config.setConnectionTimeout(30000);            // 30 seconds
            config.setValidationTimeout(5000);            // 5 seconds
            config.setMaxLifetime(1800000);               // 30 minutes
            config.setIdleTimeout(600000);                // 10 minutes
            config.setLeakDetectionThreshold(30000);      // 1 minute
            config.setConnectionTestQuery("SELECT 1");     // Simple validation query
            config.addHealthCheckProperty("connectivityCheckTimeoutMs", "1000");
            // Enable HikariCP debug logging
            config.setMetricRegistry(null); // Disable metrics to reduce noise
            config.setRegisterMbeans(true); // Enable JMX monitoring
            config.setPoolName("MainPool"); // Name the pool for easier identification in logs
            
            // Set detailed logging
            Properties logProps = new Properties(); 
            logProps.setProperty("logger", "com.zaxxer.hikari");
            logProps.setProperty("logLevel", "DEBUG");
            config.setHealthCheckProperties(logProps);

            // Update HikariCP configuration with failover-specific settings
            config.setInitializationFailTimeout(60000);    // 1 minute to wait for initialization
            config.setConnectionTimeout(30000);            // 30 seconds
            config.setValidationTimeout(5000);             // 5 seconds

            // Add specific PostgreSQL properties for failover handling
            Properties dsProps = new Properties();
            dsProps.setProperty("tcpKeepAlive", "true");
            dsProps.setProperty("socketTimeout", "30");    // 30 seconds
            dsProps.setProperty("connectTimeout", "10");   // 10 seconds
            dsProps.setProperty("loginTimeout", "10");     // 10 seconds
            dsProps.setProperty("cancelSignalTimeout", "10"); // 10 seconds
            config.setDataSourceProperties(dsProps);

            System.out.println("Connecting to datasource at " + host + " on DB " + database_name);
            ds = new HikariDataSource(config);
            final JedisPoolConfig poolConfig = RedisConfig.buildPoolConfig();
            pool = new JedisPool(poolConfig, redis_host, redis_port, redis_username, redis_password);
            Object confObj = configparser.parse(new FileReader(clientConfigPath.toString()));
            JSONObject confJsonObject = (JSONObject) confObj;
            token = (String) confJsonObject.get("discord-token");
            da_id = (String) confJsonObject.get("da-client-id");
            da_secret = (String) confJsonObject.get("da-secret");
            Object glconfObj = configparser.parse(new FileReader(globalConfigPath.toString()));
            JSONObject glconfJsonObject = (JSONObject) glconfObj;

        }
        catch (Exception e) {
            System.out.println("Error: " + e.getMessage());
            String eventId = Sentry.captureException(e).toString();
            System.out.println("Sentry error sent with ID: " + eventId);
        }
        System.out.println("Logging into Discord");
        try {
            api = new DiscordApiBuilder().setToken(token).setIntents(Intent.GUILDS).login().join();
        }
        catch(Exception ex)
        {
            ex.printStackTrace();
            System.out.println("Breakpoint");
        }
        System.out.println("Setting up RabbitMQ");
        initializeRabbitMQ();
        System.out.println("RabbitMQ setup complete");

        //Runnable's cannot touch do_id or da_secret directly, therefore we have to declare some sort of finality.
        String finalDa_id = da_id;
        String finalDa_secret = da_secret;
        Runnable da_token_task = () -> {
            try {
                System.out.println("Grabbing DeviantArt Token");
                da_token.set(daParser.getToken(finalDa_id, finalDa_secret));
                System.out.println("Token: " + da_token.get());
                System.out.println("Finished");
            } catch (Exception e) {
                System.out.println("Error refreshing DA token: " + e.getMessage());
                String eventId = Sentry.captureException(e).toString();
                System.out.println("DA token refresh error logged with ID: " + eventId);
            }
        };

        // Run it once immediately on a separate thread
        executorManager.getScheduledExecutor().submit(da_token_task);

        // Then schedule it for periodic execution
        executorManager.getScheduledExecutor().scheduleWithFixedDelay(
            da_token_task,
            0,  // initial delay of 0 means run immediately
            3600,  // then every hour
            TimeUnit.SECONDS
        );

        Runnable notification_task = () -> {
            String test_sql = "SELECT fromgroupuser, channelid, artist, foldername, deviation_link, img_url, pp_url," +
                    "mature_only from deviantcord.deviation_notifications where inverse = false";
            String inverse_sql = "SELECT fromgroupuser, channelid, artist, foldername, deviation_link, img_url, pp_url," +
                    "mature_only from deviantcord.deviation_notifications WHERE inverse = true ORDER BY notif_creation DESC";
            String journal_sql = "SELECT channelid, artist, pp_url, title, id, url, thumbnail, mature" +
                    "FROM deviantcord.journal_notifications";
            String status_sql = "SELECT artist, pp_url, url, body, thumbnail, channelid " +
                    "FROM deviantcord.status_notifications";
            Connection testcon = null;
            try {
                testcon = ds.getConnection();
                Statement stmt = testcon.createStatement();
                ResultSet rs = stmt.executeQuery(test_sql);
                System.out.println("Sending Deviations for non-inverse");
                notificationManager.sendDeviations(ds, api,rs);
                System.out.println("Sending deviations for inverse");
                stmt = testcon.createStatement();
                rs = stmt.executeQuery(inverse_sql);
                notificationManager.sendDeviations(ds, api, rs);

                testcon.close();
            } catch (SQLException e) {
                e.printStackTrace();
            }

            System.out.println("Running Notification Tasks");
        };
        
        SlashCommandRegistrar commandRegistrar = new SlashCommandRegistrar(api);
        commandRegistrar.registerCommands();

        System.out.println("Token: " + da_token.get());
        System.out.println("Finished setting up DeviantCord");
        //TODO Here needs to be investigated for null token
        
        api.addMessageComponentCreateListener(event -> {
            MessageComponentInteraction messageComponentInteraction = event.getMessageComponentInteraction();
            messageComponentInteraction.respondLater();
            String customId = messageComponentInteraction.getCustomId();
            
            // Use the existing commandExecutor instead of default ForkJoinPool
            executorManager.getCommandExecutor().submit(() -> {
                try {
                    commandRouter.routeCommand(
                        customId, 
                        messageComponentInteraction, 
                        ds,
                        pool, 
                        da_token.get(),
                        api
                    );
                } catch (SQLException | IOException | ClassNotFoundException e) {
                    messageComponentInteraction.createFollowupMessageBuilder()
                        .setContent("An error occurred processing your request.")
                        .setFlags(MessageFlag.EPHEMERAL)
                        .send();
                    String eventId = Sentry.captureException(e).toString();
                    System.out.println("Database error logged with ID: " + eventId);
                }
            });
        });
        
        api.addServerJoinListener(new ServerJoinListener() {
            @Override
            public void onServerJoin(ServerJoinEvent serverJoinEvent) {
                String new_sql = SQLManager.grab_sql("new_server");
                try {
                    Connection new_con = ds.getConnection();
                    PreparedStatement pstmt = new_con.prepareStatement(new_sql);
                    pstmt.setLong(1, serverJoinEvent.getServer().getId());
                    pstmt.setString(2,"none");
                    pstmt.setBoolean(3, false);
                    pstmt.setLong(4, 0);
                    pstmt.executeUpdate();
                    new_con.commit();
                    new_con.close();
                } catch (SQLException e) {
                    throw new RuntimeException(e);
                }
            }
        });
        api.addServerLeaveListener(new ServerLeaveListener() {
            @Override
            public void onServerLeave(ServerLeaveEvent serverLeaveEvent) {
               long server_id = serverLeaveEvent.getServer().getId();
               
               try {
                String delete_sql = SQLManager.grab_sql("delete_server_listeners");
                Connection delete_con = ds.getConnection();
                PreparedStatement pstmt = delete_con.prepareStatement(delete_sql);
                pstmt.setLong(1, server_id);
                pstmt.executeUpdate();
                delete_sql = SQLManager.grab_sql("delete_server_journal");
                pstmt = delete_con.prepareStatement(delete_sql);
                pstmt.setLong(1, server_id);
                pstmt.executeUpdate();
                delete_sql = SQLManager.grab_sql("delete_server_config");
                pstmt = delete_con.prepareStatement(delete_sql);
                pstmt.setLong(1, server_id);
                pstmt.executeUpdate();
                delete_con.commit();
                delete_con.close();
               } catch (SQLException e) {
                String eventId = Sentry.captureException(e).toString();
                System.out.println("Database error logged with ID: " + eventId);
                try {
                    FileWriter fw = new FileWriter("IMPORTANT_missed_deletes.txt", true);
                    BufferedWriter bw = new BufferedWriter(fw);
                    bw.write("Failed to delete server: " + server_id + " (Event ID: " + eventId + ")\n");
                    bw.close();
                } catch (IOException ioe) {
                    String ioEventId = Sentry.captureException(ioe).toString();
                    System.out.println("IO error logged with ID: " + ioEventId);
                }
                throw new RuntimeException(e);
               }
            }
        });
        System.out.println("Setting up Command Handler");
        CommandHandler commandHandler = new CommandHandler(
            executorManager, 
            ds, 
            pool, 
            da_token, 
            api
        );
        System.out.println("Command Handler setup complete");
        api.addSlashCommandCreateListener(event -> {
            commandHandler.handleCommand(event.getSlashCommandInteraction());
        });
    }


}
