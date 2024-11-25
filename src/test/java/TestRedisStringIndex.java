import org.errite.deviantcord.sd.redisStringParser;

import java.util.HashMap;
import java.util.UUID;

public class TestRedisStringIndex {

    public static void main(String[] args) {
        String uuid = UUID.randomUUID().toString() +"START-:-";
        String testResponse = uuid + "848764576832028682FI-:-XAEL-THE-ARTISTFI-:-All Folder";
        HashMap<String, String> responseProperties = new HashMap<>();
        responseProperties = redisStringParser.parseRedisString(testResponse);
    }
}
