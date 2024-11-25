import java.util.HashMap;
import org.errite.deviantcord.sd.commandIdParser;

public class CheckDeleteFolderCommandId {

    public static void main(String[] args) {
    
        String responseId = "dfFI-:-849066327649943563FI-:-XAEL-THE-ARTISTFI-:-ALL FOLDER";
        HashMap<String, String> responseProperties = commandIdParser.parseNonChannelReplaceString(responseId);
        System.out.println(responseProperties.get("channel"));
        System.out.println(responseProperties.get("artist"));
        System.out.println(responseProperties.get("folder"));
    }
}