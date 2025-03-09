import org.errite.deviantcord.sd.commandIdParser;

import java.util.HashMap;
import java.util.UUID;

public class testParsePageString {

    public static void main(String[] args) {

        UUID uuid = UUID.randomUUID();
        String uuid_string = uuid.toString();
        String test_id = "npFI-:-30b1a925-cbf9-4bd4-abad-d4ae08815db0FI-:-575459125232795652";
        HashMap<String, String> properties = commandIdParser.parsePageString(test_id);
        String obtUuid = properties.get("uuid");
        String obtServerId = properties.get("serverid");
        System.out.println(obtUuid);
        System.out.println(obtServerId);
    }
}
