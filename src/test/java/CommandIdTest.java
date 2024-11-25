import org.errite.deviantcord.sd.commandId;
import org.errite.deviantcord.sd.commandIdParser;

import java.util.HashMap;

public class CommandIdTest {

    public static void main(String[] args) {

        String str = "uiFI-:-211349864133558272FI-:-Xael-TheArtistFI-:-All FolderFI-:-759461677510557726FI-:-292120646337560579";
        Enum<commandId.Command> obtCommand = commandId.parseCommand(str);
        HashMap<String, String> obtInfo = commandIdParser.parseChannelReplaceString(str);
        System.out.println("Breakpoiunt");

    }
}
