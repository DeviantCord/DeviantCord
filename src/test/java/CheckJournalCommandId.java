import java.util.HashMap;
import org.errite.deviantcord.sd.commandIdParser;

public class CheckJournalCommandId {

    public static void main(String[] args) {
        String commandId = "ajmFI-:-575459125698232341FI-:-Xael-The-ArtistFI-:-";
        HashMap<String, String> properties = commandIdParser.parseAddJournalString(commandId);
        System.out.println(properties);
    }
}
