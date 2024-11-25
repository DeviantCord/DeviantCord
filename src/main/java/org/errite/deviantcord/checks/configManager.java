package org.errite.deviantcord.checks;

import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import org.json.JSONObject;
public class configManager {
    // ... existing help method ...

    public static void checkClientConfig() {
        File configFile = new File("client.json");
        if (!configFile.exists()) {
        try {
            JSONObject baseConfig = new JSONObject();
            baseConfig.put("da-client-id", "");
            baseConfig.put("da-secret", "");
            baseConfig.put("discord-token", "");
            
            FileWriter writer = new FileWriter(configFile);
            writer.write(baseConfig.toString(4)); // pretty print with 4 space indentation
            writer.close();
            
            System.out.println("Created default client.json configuration file");
        } catch (IOException e) {
            System.err.println("Error creating client.json: " + e.getMessage());
        }
        }
    }

    // ... existing code ...

public static void checkConfig() {
    File configFile = new File("config.json");
    if (!configFile.exists()) {
        try {
            JSONObject baseConfig = new JSONObject();
            baseConfig.put("use_sentry", false);
            baseConfig.put("sentry_dsn", "");
            
            FileWriter writer = new FileWriter(configFile);
            writer.write(baseConfig.toString(4)); // pretty print with 4 space indentation
            writer.close();
            
            System.out.println("Created default config.json configuration file");
        } catch (IOException e) {
            System.err.println("Error creating config.json: " + e.getMessage());
        }
    }
}

// ... existing code ...


    
}
