package org.errite.deviantcord.cmds;

import org.json.simple.JSONObject;
import org.json.simple.parser.JSONParser;
import org.json.simple.parser.ParseException;

import org.javacord.api.DiscordApi;

public class rabbitRouter {

    
    public static void routeMessage(String message, DiscordApi api){
        try {
            JSONParser parser = new JSONParser();
            JSONObject jsonObject = (JSONObject) parser.parse(message);
            
            String notificationType = (String) jsonObject.get("notification_type");
            if (notificationType.toLowerCase().equals("deviation") ) {
                rabbitCommands.sendDeviation(message, api, jsonObject);
            }
            else if (notificationType.toLowerCase().equals("journal")) {
                rabbitCommands.sendJournal(message, api, jsonObject);
            }
        } catch (ParseException e) {
            System.err.println("Error parsing JSON: " + e.getMessage());
            // Handle the exception as needed
        }
        
    }
}
