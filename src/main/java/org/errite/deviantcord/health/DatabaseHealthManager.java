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
package org.errite.deviantcord.health;

import com.zaxxer.hikari.HikariConfig;
import com.zaxxer.hikari.HikariDataSource;
import com.zaxxer.hikari.HikariPoolMXBean;
import io.sentry.Sentry;
import org.json.simple.JSONObject;
import org.json.simple.parser.JSONParser;

import java.io.FileReader;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.sql.*;
import java.util.Properties;
import java.util.concurrent.TimeUnit;

public class DatabaseHealthManager {
    private HikariDataSource ds;
    private final Path configPath;
    private final Properties dbProperties;

    public DatabaseHealthManager(HikariDataSource dataSource) {
        this.ds = dataSource;
        // Initialize config path - adjust this based on your project structure
        this.configPath = Paths.get("config", "config.json");
        this.dbProperties = new Properties();
        loadDatabaseProperties();
    }

    private void loadDatabaseProperties() {
        try {
            JSONParser parser = new JSONParser();
            JSONObject config = (JSONObject) parser.parse(new FileReader(configPath.toFile()));
            JSONObject database = (JSONObject) config.get("database");

            dbProperties.setProperty("jdbcUrl", (String) database.get("url"));
            dbProperties.setProperty("username", (String) database.get("username"));
            dbProperties.setProperty("password", (String) database.get("password"));
            // Add any other properties you need
        } catch (Exception e) {
            Sentry.captureException(e);
            throw new RuntimeException("Failed to load database properties", e);
        }
    }

    public void checkHealth() {
        try (Connection conn = ds.getConnection()) {
            try (Statement stmt = conn.createStatement()) {
                stmt.execute("SELECT 1");
            }
        } catch (SQLException e) {
            handleHealthCheckFailure(e);
        }
    }

    private void handleHealthCheckFailure(SQLException e) {
        System.out.println("Database health check failed: " + e.getMessage());
        String eventId = Sentry.captureException(e).toString();
        System.out.println("Database health check error logged with ID: " + eventId);

        if (isFailoverRelated(e)) {
            try {
                refreshConnectionPool();
            } catch (Exception refreshException) {
                String refreshEventId = Sentry.captureException(refreshException).toString();
                System.out.println("Connection pool refresh error logged with ID: " + refreshEventId);
            }
        } else {
            logPoolStatistics();
        }
    }

    private boolean isFailoverRelated(SQLException e) {
        String message = e.getMessage().toLowerCase();
        return message.contains("failover") || 
               message.contains("connection refused") || 
               message.contains("connection reset") ||
               message.contains("connection closed");
    }

    private void refreshConnectionPool() {
        System.out.println("Attempting to refresh connection pool...");
        
        // Close existing pool
        if (ds != null && !ds.isClosed()) {
            ds.close();
        }

        // Create new configuration
        HikariConfig config = new HikariConfig();
        config.setJdbcUrl(dbProperties.getProperty("jdbcUrl"));
        config.setUsername(dbProperties.getProperty("username"));
        config.setPassword(dbProperties.getProperty("password"));
        
        // Add any other configuration properties you need
        config.setMaximumPoolSize(20);
        config.setMinimumIdle(5);
        
        // Create new datasource
        HikariDataSource newDs = new HikariDataSource(config);
        
        // Test the new connection
        try (Connection conn = newDs.getConnection()) {
            try (Statement stmt = conn.createStatement()) {
                stmt.execute("SELECT 1");
            }
            // If successful, update the datasource reference
            this.ds = newDs;
            System.out.println("Successfully refreshed connection pool");
        } catch (SQLException e) {
            newDs.close(); // Clean up if test failed
            throw new RuntimeException("Failed to establish connection with new pool", e);
        }
    }

    private void logPoolStatistics() {
        HikariPoolMXBean poolMXBean = ds.getHikariPoolMXBean();
        if (poolMXBean != null) {
            System.out.println("Pool Stats - Active: " + poolMXBean.getActiveConnections() +
                             ", Idle: " + poolMXBean.getIdleConnections() +
                             ", Waiting: " + poolMXBean.getThreadsAwaitingConnection() +
                             ", Total: " + poolMXBean.getTotalConnections());
        }
    }
} 