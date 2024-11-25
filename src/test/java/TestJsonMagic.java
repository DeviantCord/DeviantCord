import io.restassured.response.Response;
import org.errite.deviantcord.da.daParser;
import org.errite.deviantcord.types.JournalObject;

import java.util.*;

public class TestJsonMagic {

    public static void main(String[] args) {
        int appId = 9616;
        Scanner secretScanner = new Scanner(System.in);
        System.out.println("Please enter the DA Secret for this test");
        String secret = secretScanner.nextLine();
        String token = daParser.getToken(String.valueOf(appId), secret);
        Response journalTest = daParser.getJournals("Zander-The-Artist", token,true, false, 12);
        JournalObject obtJournals = new JournalObject();
        ArrayList<LinkedHashMap> node = journalTest.jsonPath().getJsonObject("results");
        Iterator<LinkedHashMap> iterator = node.iterator();
        while(iterator.hasNext()){
            boolean foundThumb = false;
            LinkedHashMap entry = iterator.next();
            System.out.println(entry.get("thumbs").getClass());
            obtJournals.appendDeviationId((String)entry.get("deviation-id"));
            obtJournals.appendJournalUrls((String)entry.get("url"));
            obtJournals.appendTitle((String) entry.get("title"));
            ArrayList<LinkedHashMap> obt_thumbs = (ArrayList<LinkedHashMap>) entry.get("thumbs");


        }

    }
}
