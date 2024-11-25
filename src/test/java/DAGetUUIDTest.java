import org.errite.deviantcord.da.daParser;
import org.json.simple.JSONObject;
import org.json.simple.parser.JSONParser;
import org.json.simple.parser.ParseException;

import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.IOException;
import java.nio.file.Path;
import java.nio.file.Paths;

public class DAGetUUIDTest
{
    public static void main(String[] args) throws IOException, ParseException {
        Path currentPath = Paths.get(System.getProperty("user.dir"));
        Path clientConfigPath = Paths.get(currentPath.toString(),"client.json");
        JSONParser configparser = new JSONParser();
        Object confObj = configparser.parse(new FileReader(clientConfigPath.toString()));
        JSONObject confJsonObject = (JSONObject) confObj;
        String token = (String) confJsonObject.get("discord-token");
        String da_id = (String) confJsonObject.get("da-client-id");
        String da_secret = (String) confJsonObject.get("da-secret");
        String da_token = daParser.getToken(da_id, da_secret);
        String uuid = daParser.getFolderUUID("Xael-The-Artist","Aezae's Tales",da_token, true );
    }
}
